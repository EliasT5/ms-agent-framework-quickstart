"""
Unit 5 — Installing MCP plugins & skills.

Three parts:
  A. local stdio MCP plugin (calculator)
  B. remote HTTP MCP plugin (Microsoft Learn)
  C. both MCP plugins + a custom function tool on one agent

Run: python agent.py
"""

import asyncio
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Annotated

# Windows cp1252 stdout can't encode the → ← in middleware logs — reconfigure.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from agent_framework import (
    FunctionInvocationContext,
    MCPStdioTool,
    MCPStreamableHTTPTool,
    function_middleware,
)
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

NOTES_DIR = Path(__file__).parent / "notes"


def _args_to_dict(args) -> dict:
    """Coerce FunctionInvocationContext.arguments (BaseModel or Mapping) into a plain dict."""
    if args is None:
        return {}
    if hasattr(args, "model_dump"):
        return args.model_dump()
    try:
        return dict(args)
    except (TypeError, ValueError):
        return {"_repr": str(args)}


# --- A custom Python function tool, used in Part C -----------------------


def save_note(
    title: Annotated[str, Field(description="Short kebab-case title used for the filename.")],
    content: Annotated[str, Field(description="Markdown content to save.")],
) -> str:
    """Save a note as a Markdown file to the local notes/ folder."""
    NOTES_DIR.mkdir(exist_ok=True)
    path = NOTES_DIR / f"{title}.md"
    path.write_text(content, encoding="utf-8")
    return f"saved to {path}"


# --- Middleware used in Part C to watch tool routing ---------------------


@function_middleware
async def log_tool_calls(
    context: FunctionInvocationContext,
    call_next: Callable[[], Awaitable[None]],
) -> None:
    name = context.function.name
    args = _args_to_dict(context.arguments)
    print(f"  [→] {name}({args})")
    await call_next()
    result_str = str(context.result)[:120]
    print(f"  [←] {name} → {result_str}")


# --- Part A: local MCP plugin (stdio) ------------------------------------


async def part_a_local_calculator() -> None:
    print("=" * 60)
    print("Part A — local MCP plugin: calculator (stdio)")
    print("=" * 60)

    async with MCPStdioTool(
        name="calculator",
        command="uvx",
        args=["mcp-server-calculator"],
        load_prompts=False,  # server has no prompts
    ) as calc_tool:
        agent = OpenAIChatCompletionClient().as_agent(
            name="MathAgent",
            instructions=(
                "You are a precise math assistant. Use the calculator tool "
                "for any arithmetic. Show the result plainly."
            ),
            tools=[calc_tool],
        )

        result = await agent.run("What is 23 * 47 + 113?")
        print(f"Agent: {result.text}\n")


# --- Part B: remote MCP plugin (HTTP) ------------------------------------


async def part_b_remote_mslearn() -> None:
    print("=" * 60)
    print("Part B — remote MCP plugin: Microsoft Learn (HTTP)")
    print("=" * 60)

    async with MCPStreamableHTTPTool(
        name="ms-learn",
        url="https://learn.microsoft.com/api/mcp",
        load_prompts=False,  # server has no prompts
    ) as learn_tool:
        agent = OpenAIChatCompletionClient().as_agent(
            name="DocsAgent",
            instructions=(
                "You answer Microsoft tooling questions using the Microsoft Learn "
                "MCP tool for grounded, up-to-date information. Cite any doc "
                "snippets you use."
            ),
            tools=[learn_tool],
        )

        result = await agent.run(
            "How do I create an Azure storage account using the az CLI? "
            "Give me the command, not a long explanation."
        )
        print(f"Agent: {result.text}\n")


# --- Part C: combine both plugins + a custom tool ------------------------


async def part_c_combined() -> None:
    print("=" * 60)
    print("Part C — calculator + MS Learn + save_note, with middleware")
    print("=" * 60)

    async with (
        MCPStdioTool(name="calculator", command="uvx", args=["mcp-server-calculator"], load_prompts=False) as calc_tool,
        MCPStreamableHTTPTool(name="ms-learn", url="https://learn.microsoft.com/api/mcp", load_prompts=False) as learn_tool,
    ):
        agent = OpenAIChatCompletionClient().as_agent(
            name="StudyBuddy",
            instructions=(
                "You help the user study cloud topics. "
                "Use the calculator for arithmetic, the Microsoft Learn tool "
                "for Azure/MS questions, and save_note to persist summaries "
                "the user asks you to remember. Keep answers concise."
            ),
            tools=[calc_tool, learn_tool, save_note],
            middleware=[log_tool_calls],
        )

        session = agent.create_session()

        prompts = [
            "What is 500 * 23?",
            "How do I list all Azure Function apps in a subscription with the az CLI?",
            "Save that as a note titled 'list-azure-functions'.",
        ]
        for p in prompts:
            print(f"\nUser: {p}")
            print("Tool calls:")
            r = await agent.run(p, session=session)
            print(f"Agent: {r.text}")


async def main() -> None:
    await part_a_local_calculator()
    await part_b_remote_mslearn()
    await part_c_combined()


if __name__ == "__main__":
    asyncio.run(main())
