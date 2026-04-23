"""
Unit 7 — Capstone: a verbose coding agent.

Everything you've learned, put together:
- Custom function tools (Unit 2)
- Multi-step agentic loop via agent.run() (Unit 3)
- Function middleware logging every tool call in real time (Unit 3)
- Conversation memory via AgentSession (Unit 4)
- @tool(approval_mode="always_require") on dangerous tools (Unit 6)
- System prompt that makes the agent narrate its reasoning

The agent runs in NON-streaming mode. Streaming tool calls are flaky
across providers/proxies — many emit tool-call JSON into the content
stream instead of into structured tool_call deltas, which turns "watch
the agent think" into "watch the agent print garbage". Middleware
gives live per-tool visibility without needing the stream.

This unit does NOT use the MCP filesystem plugin by default. The 4 custom
tools below cover read/list/write/shell. Adding MCP on top made the model
mix tool choices and hit MCP's "path must be absolute under allowed dir"
rule (it rejects `.` even when `.` is the allowed dir). See the README
for how to add it back if you want.

Run: python agent.py
"""

import asyncio
import json
import re
import subprocess
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Annotated, Any

from agent_framework import (
    AgentResponse,
    FunctionInvocationContext,
    Message,
    function_middleware,
    tool,
)
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

# Windows default stdout is cp1252 — can't encode → ← in middleware logs.
# A UnicodeEncodeError in middleware surfaces as a tool failure to the agent.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------------
# Sandbox
# ------------------------------------------------------------------------

WORKSPACE = (Path(__file__).parent / "workspace").resolve()
WORKSPACE.mkdir(exist_ok=True)


def _args_to_dict(args) -> dict:
    if args is None:
        return {}
    if hasattr(args, "model_dump"):
        return args.model_dump()
    try:
        return dict(args)
    except (TypeError, ValueError):
        return {"_repr": str(args)}


def _safe_path(path: str) -> Path:
    candidate = (WORKSPACE / path).resolve()
    if WORKSPACE not in candidate.parents and candidate != WORKSPACE:
        raise ValueError(f"path {path!r} escapes the sandbox")
    return candidate


# ------------------------------------------------------------------------
# Tools
# ------------------------------------------------------------------------


PATH_DESC = (
    "A relative path like 'primes.py' or 'src/utils.py'. "
    "DO NOT include a leading '/' or the workspace folder name — "
    "the tool automatically resolves the path inside the sandboxed workspace. "
    "Use '.' to mean the workspace root itself."
)

COMMAND_DESC = (
    "A shell command. It runs with the workspace as the current directory, "
    "so use plain filenames like 'python primes.py', not absolute paths."
)


@tool(approval_mode="never_require")
def read_file(
    path: Annotated[str, Field(description=PATH_DESC)],
) -> str:
    """Read a text file from the workspace."""
    p = _safe_path(path)
    if not p.exists():
        return f"error: {path} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


@tool(approval_mode="never_require")
def list_dir(
    path: Annotated[str, Field(description=PATH_DESC)] = ".",
) -> str:
    """List files and folders in a workspace directory."""
    p = _safe_path(path)
    if not p.exists():
        return f"error: {path} does not exist"
    if not p.is_dir():
        return f"error: {path} is not a directory"
    entries = sorted(p.iterdir(), key=lambda e: (not e.is_dir(), e.name))
    lines = [f"{'dir' if e.is_dir() else 'file'}  {e.name}" for e in entries]
    return "\n".join(lines) if lines else "(empty)"


@tool(approval_mode="always_require")
def write_file(
    path: Annotated[str, Field(description=PATH_DESC)],
    content: Annotated[str, Field(description="Complete file contents to write.")],
) -> str:
    """Create or overwrite a file in the workspace. Requires user approval."""
    p = _safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"wrote {len(content)} bytes to {path}"


@tool(approval_mode="always_require")
def run_shell(
    command: Annotated[str, Field(description=COMMAND_DESC)],
) -> str:
    """Run a shell command inside the workspace. Requires user approval."""
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return "error: command timed out after 60s"
    out = (completed.stdout or "") + (completed.stderr or "")
    return f"exit={completed.returncode}\n{out[-2000:]}"


# ------------------------------------------------------------------------
# Middleware — prints every tool call as it happens
# ------------------------------------------------------------------------

DIM = "\033[90m"
BOLD = "\033[1m"
YELLOW = "\033[33m"
RED = "\033[91m"
RESET = "\033[0m"


def _format_result(result) -> str:
    """Extract a readable string from a tool result (framework wraps it in
    Content objects before handing it to the middleware post-call)."""
    if result is None:
        return "None"
    if isinstance(result, str):
        return result
    if isinstance(result, list):
        parts = []
        for item in result:
            for attr in ("result", "text"):
                v = getattr(item, attr, None)
                if v is not None:
                    parts.append(str(v))
                    break
            else:
                parts.append(str(item))
        return " | ".join(parts)
    return str(result)


# Track which tools actually got invoked this turn, so we can compare
# against what the agent *claims* it did.
TOOLS_CALLED_THIS_TURN: set[str] = set()


@function_middleware
async def log_tool_calls(
    context: FunctionInvocationContext,
    call_next: Callable[[], Awaitable[None]],
) -> None:
    name = context.function.name
    TOOLS_CALLED_THIS_TURN.add(name)
    args = _args_to_dict(context.arguments)
    short_args = {
        k: (str(v)[:60] + "..." if len(str(v)) > 60 else v) for k, v in args.items()
    }
    print(f"{DIM}  [tool →] {name}({short_args}){RESET}", flush=True)
    await call_next()
    result_str = _format_result(context.result)[:200].replace("\n", " ")
    print(f"{DIM}  [tool ←] {name} → {result_str}{RESET}", flush=True)


# ------------------------------------------------------------------------
# Sanity check: detect when the model emits tool calls as plain TEXT
# instead of structured function calls. Happens when the LiteLLM proxy +
# model combo doesn't translate the tool-use format into OpenAI's
# function-calling protocol. Classic symptom: the agent claims it wrote
# or ran a file, but no [tool →] log appeared and nothing actually happened.
# ------------------------------------------------------------------------

# Match leaked tool-call JSON in content. Covers three forms we've seen:
#   {"tool_calls": [{"name": "...", ...}]}      — full wrapper
#   {"name": "write_file", "arguments": {...}}  — unwrapped call
#   {"path": "...", "content": "..."}           — bare arguments
FAKE_TOOL_CALL_PATTERNS = [
    re.compile(r'\{["\']tool_calls?["\']\s*:', re.DOTALL),
    re.compile(r'\{["\']name["\']\s*:\s*["\'](?:read_file|list_dir|write_file|run_shell)', re.DOTALL),
    re.compile(r'\{["\']path["\']\s*:\s*["\'][^"\']+["\']\s*,\s*["\']content["\']\s*:', re.DOTALL),
    re.compile(r'\{["\']command["\']\s*:\s*["\'][^"\']+["\']\s*\}', re.DOTALL),
]


def warn_if_fake_tool_calls(text: str, tools_actually_called: set[str]) -> None:
    """Print a loud warning if the agent's response contains tool-call JSON
    as text — and especially if no real tool calls happened."""
    if not text:
        return
    if not any(p.search(text) for p in FAKE_TOOL_CALL_PATTERNS):
        return
    print(
        f"\n{RED}{'=' * 70}\n"
        f"[warn] the agent's reply contains tool-call JSON as PLAIN TEXT.\n"
        f"       nothing was actually executed for those calls.\n"
        f"       real tool calls this turn: "
        f"{sorted(tools_actually_called) or 'none'}\n\n"
        f"       root cause: your LiteLLM proxy + model combo isn't emitting\n"
        f"       tool_calls in OpenAI function-calling format. Fix it in\n"
        f"       your litellm config (mark model tool-calling-capable, or\n"
        f"       enable add_function_to_prompt) — not in the curriculum code.\n"
        f"{'=' * 70}{RESET}",
        flush=True,
    )


# ------------------------------------------------------------------------
# Approval loop
# ------------------------------------------------------------------------


async def run_with_approvals(
    query: str | list[Any],
    agent,
    session,
    max_rounds: int = 20,
) -> AgentResponse:
    result = await agent.run(query, session=session)

    rounds = 0
    while result.user_input_requests:
        rounds += 1
        if rounds > max_rounds:
            raise RuntimeError(
                f"Exceeded {max_rounds} approval rounds — check your provider/proxy setup."
            )

        responses: list[Any] = []
        for request in result.user_input_requests:
            fn = request.function_call
            args_preview = str(fn.arguments)
            if len(args_preview) > 300:
                args_preview = args_preview[:300] + "..."
            print(f"\n{YELLOW}  Approval requested{RESET}")
            print(f"    function: {fn.name}")
            print(f"    args:     {args_preview}")
            answer = await asyncio.to_thread(input, "  Approve? (y/n): ")
            approved = answer.strip().lower().startswith("y")
            responses.append(
                Message("user", [request.to_function_approval_response(approved)])
            )

        result = await agent.run(responses, session=session)

    return result


# ------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------

INSTRUCTIONS = """\
You are a careful coding assistant with a sandboxed work folder.
All your file tools operate inside a hidden sandbox — you do NOT need to know
its location. Just pass plain filenames like 'primes.py' or relative paths like
'src/utils.py' to read_file / list_dir / write_file. The tools resolve the
path for you. The shell runs with the sandbox as its working directory.

HARD RULE — when the user asks for a file, YOU PICK THE FILENAME and call
write_file immediately. Do NOT ask the user "where should I put it?" — the
answer is always the sandbox, and the tool handles it.

Examples of what to do:
- User: "write a fizzbuzz script"            → call write_file(path='fizzbuzz.py', content=...)
- User: "create tests for calc.py"           → call write_file(path='test_calc.py', content=...)
- User: "save it somewhere"                  → call write_file(path='<a reasonable filename>.py', content=...)
- User: "run the script"                     → call run_shell(command='python <filename>.py')

You have real tools — call them, don't narrate them. If your reply ever
contains text like {"path":"..."} or {"tool_calls":[...]} you have failed;
use the actual tool call instead.

Workflow:
- Before writing over an existing file, read_file it first.
- After writing code, run_shell to verify it works and report pass/fail.
- Narrate briefly (one short sentence) before each tool call and one after.
- Don't fabricate tool results. If a tool fails, say exactly what the error was.
"""


async def main() -> None:
    print(f"workspace: {WORKSPACE}\n")
    print("Coding agent ready. Type a task, or 'quit' to exit.")
    print("Example: Create hello.py that prints 'hi', then run it.\n")

    agent = OpenAIChatCompletionClient().as_agent(
        name="CodingAgent",
        instructions=INSTRUCTIONS,
        tools=[read_file, list_dir, write_file, run_shell],
        middleware=[log_tool_calls],
    )

    session = agent.create_session()

    while True:
        try:
            user = await asyncio.to_thread(input, "\nyou > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user.strip():
            continue
        if user.strip().lower() in {"quit", "exit", "bye"}:
            print("bye.")
            break

        TOOLS_CALLED_THIS_TURN.clear()
        try:
            result = await run_with_approvals(user, agent, session)
        except Exception as exc:
            print(f"\n[error] {type(exc).__name__}: {exc}")
            continue

        print(f"\n{BOLD}{agent.name}:{RESET} {result.text}")
        warn_if_fake_tool_calls(result.text, TOOLS_CALLED_THIS_TURN.copy())


if __name__ == "__main__":
    asyncio.run(main())
