# Unit 7 — Capstone: a verbose coding agent ⭐

## What this is

A working prototype of a coding agent — the same shape as Copilot CLI, Aider, or Claude Code — built from everything you've learned, wired up to feel like a real product:

- **Live tool logging** — middleware prints `[tool →] name(args)` and `[tool ←] result` around every call in grey, so you watch the agent's decisions as they happen.
- **Thought-process narration** — the agent is instructed to say one short sentence before each tool call explaining what it's about to do, and one after about what it learned. That text appears in the final response alongside the logs.
- **Inline approvals** — when it wants to write a file or run a command, you get a y/n prompt; the agent resumes after your answer.
- **Non-streaming run-mode** — the agent runs with `stream=False` on purpose. Streaming + tool calls is brittle across providers: many LiteLLM-backed models emit tool-call JSON into the content delta instead of structured tool_call deltas, which prints `{"path":...}` gibberish in the middle of the response. Non-streaming uses the fully-resolved response format; middleware still gives you live per-tool visibility.

The agent can:

- **Read** files in a sandboxed `workspace/` folder (safe, no approval).
- **List** directory contents (safe, no approval).
- **Write** files (⚠️ requires approval).
- **Run shell commands** (⚠️ requires approval).

It remembers the conversation via `AgentSession`, so you can say "now add tests" after it writes `fizz.py`.

> The filesystem MCP plugin is deliberately not wired in by default. See "Adding the filesystem MCP plugin" below for why and how to add it back.

## Why it matters

This is the end goal: a real coding agent, in ~200 lines, built on Microsoft Agent Framework. It's not production-ready (see "limits" below) but it works end-to-end and the pattern is correct.

## Mental model

Most of this file is something you've already learned:

| What | From which unit |
|---|---|
| Streaming via `agent.run(..., stream=True)` | Unit 1 |
| Custom function tools | Unit 2 |
| Multi-step loop via `agent.run()` | Unit 3 |
| Middleware logging | Unit 3 |
| Conversation memory (`AgentSession`) | Unit 4 |
| MCP plugin (`MCPStdioTool` for filesystem) | Unit 5 |
| `@tool(approval_mode="always_require")` for dangerous ops | Unit 6 |

New concepts in this unit:

- **Sandboxing:** every filesystem tool resolves its path inside `workspace/` and rejects `../` escapes.
- **Graceful MCP fallback:** the filesystem MCP is wrapped in a try/except async context manager. If `npx` is missing or the package won't start, the agent runs without it instead of crashing.
- **Thought-out-loud instructions:** the system prompt tells the agent to narrate one sentence before and after each tool call. This is pure prompt engineering — no framework feature — but it's what turns a silent agent into one that feels like a collaborator.
- **UTF-8 stdout on Windows:** the middleware prints `→` / `←` which aren't in Windows' default `cp1252`. The script calls `sys.stdout.reconfigure(encoding="utf-8")` at startup — without it, the print raises `UnicodeEncodeError`, the framework interprets that as a tool failure, retries, and eventually gives up with an invented "my tools aren't working" response.

## Tool inventory

| Tool | Approval? | Purpose |
|---|---|---|
| `read_file(path)` | no | Read a text file inside `workspace/`. |
| `list_dir(path)` | no | List files/folders inside `workspace/`. |
| `write_file(path, content)` | **yes** | Create or overwrite a file inside `workspace/`. |
| `run_shell(command)` | **yes** | Run a shell command inside `workspace/`. |
| `filesystem-mcp` (MCP plugin) | no | Read-only search/grep across `workspace/`. |

## Instructions given to the agent

The system prompt is deliberately tight. It tells the agent:

1. Stay inside `workspace/`.
2. Read before you write (cheaper to check than to redo).
3. After writing code, run its tests.
4. Prefer small, reviewable changes.

## What the code does

1. Sets `WORKSPACE = Path("./workspace")` and sandboxes every filesystem tool to it.
2. Launches the `@modelcontextprotocol/server-filesystem` MCP server rooted at `workspace/` via `npx` (you need Node — see SETUP.md step 7).
3. Creates an agent with custom tools + the MCP tool + the logging middleware + a thread.
4. Drops into a REPL. You type tasks, the agent plans, asks approval for writes/shells, and iterates.

## Try this

Make sure Node is installed (`npx --version`). Then:

```powershell
python agent.py
```

Canned warm-up session (italic = streamed narration, grey = middleware tool logs, yellow = approval prompt):

```
you > Create calc.py with add, sub, mul, div; then run a quick sanity check.

CodingAgent: Let me check the workspace first.
  [tool →] list_dir({'path': '.'})
  [tool ←] list_dir → (empty)
The workspace is empty. I'll create calc.py now.
  [tool →] write_file({'path': 'calc.py', 'content': 'def add(a, b):...'})

  Approval requested
    function: write_file
    args:     {'path': 'calc.py', 'content': '...'}
  Approve? (y/n): y

  [tool ←] write_file → wrote 143 bytes to calc.py
calc.py is written. Let me verify it loads correctly.
  [tool →] run_shell({'command': 'python -c "import calc; print(calc.add(2,3))"'})

  Approval requested
    function: run_shell
    args:     {'command': 'python -c "import calc; print(calc.add(2,3))"'}
  Approve? (y/n): y

  [tool ←] run_shell → exit=0\n5
Done — add(2,3) returned 5, the four functions are in place.

you > quit
```

The `workspace/` folder now has `calc.py` and `test_calc.py` — artifacts from your conversation with the agent.

## Limits (things this is NOT)

- **Not a secure sandbox.** `run_shell` executes on your host. Don't expose this over a network without containerizing. Tools like [Aider](https://aider.chat/) and [OpenDevin](https://github.com/OpenDevin/OpenDevin) have real sandboxing you can study.
- **No diff preview.** `write_file` shows you the full content; it doesn't show a diff against the existing file. Easy addition, left as an exercise.
- **No cost controls.** Long sessions burn tokens. In production: summarize threads, set token budgets.
- **No retry/rollback.** If the agent writes broken code you have to catch it yourself. Git helps.

## Where to go next

If you want to push this further:

1. **Replace `run_shell` with a Docker-sandboxed version.** Mount `workspace/` read-write and run commands inside a disposable container.
2. **Add a diff-preview to `write_file`.** Print a unified diff before asking for approval.
3. **Add `git_*` tools.** `git_status`, `git_diff`, `git_commit` (approval-gated). Now your agent is a real collaborator.
4. **Swap to Foundry + Entra.** Change `OpenAIChatCompletionClient()` → `FoundryChatClient(project_endpoint=..., credential=AzureCliCredential())`. That's it — everything else stays the same.
5. **Learn workflows.** Graph-based multi-agent orchestration from Microsoft Agent Framework's [workflows samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows). You could split the coding agent into "planner", "writer", and "critic" nodes.

## When things break

### Agent hallucinates that it wrote/ran things (nothing actually happens)

The most common failure, and **it's not a bug in this code**. Symptom:

- The agent's reply contains JSON like `{"tool_calls":[...]}` or `{"path":"...","content":"..."}` as plain text.
- No `[tool →]` middleware log appears.
- Workspace is empty after the agent claims to have written files.

If this happens, you'll see a loud red warning at the bottom of the response. The cause: **your LiteLLM proxy + model combo isn't translating the model's tool-use into OpenAI's function-calling protocol.** The framework never sees a real tool call, so nothing runs.

**Fixes on the provider side (you, not the curriculum):**

1. **Use a model with native OpenAI-format tool calling.** In your LiteLLM config, point at something known to support it: `openai/gpt-4o-mini`, `anthropic/claude-sonnet-4-6`, `openai/gpt-4o`. Open-weights models and fine-tunes often don't emit the right format.
2. **Enable `add_function_to_prompt` in LiteLLM.** For models that can't natively emit `tool_calls`, LiteLLM can embed tool schemas in the system prompt and parse function-call-shaped responses back into the OpenAI format. See [LiteLLM: function calling](https://docs.litellm.ai/docs/completion/function_call) — search for `add_function_to_prompt`.
3. **Mark your model as tool-calling-capable.** If you're using a custom `model_list` entry, add `supports_function_calling: true`.

Test with: `python unit-00-setup\agent.py` — if that works, plain chat is fine. Then: `python unit-02-tools\agent.py` — if the weather comes back from the tool (not hallucinated), function calling works.

### Other issues

- **Agent refuses to do anything** — prompt was too vague. Try specific tasks like `"Create calc.py with add/sub/mul/div, then test it"`.
- **`UnicodeEncodeError` on Windows** — shouldn't happen (the script reconfigures stdout to UTF-8 on startup), but if you copy the middleware into your own code, do the same.
- **Approval loop feels repetitive for safe operations** — only `"always_require"` and `"never_require"` exist in the 1.1 API. For "ask-once-per-session", track approved `(function, args)` tuples in `run_with_approvals` and auto-approve repeats.
- **Agent writes outside `workspace/`** — shouldn't happen (sandboxed path resolution raises), but check the traceback if it does.

## Adding the filesystem MCP plugin (optional)

The capstone dropped the `@modelcontextprotocol/server-filesystem` MCP plugin by default because (a) the 4 custom tools cover its functionality and (b) the MCP server rejects `.` as a path — it resolves paths against the calling process's CWD and then checks them against its `--allowed-directories` list, so even "list the current directory" fails with *"Access denied — outside allowed directories"* when the model passes `.`.

To add it back anyway, reinstate the `optional_filesystem_mcp` context manager (see git history pre-simplification) and tell the agent in its instructions to always pass the absolute workspace path, not `.`.

## Sources

This unit synthesizes everything from Units 2–6. Primary references:

- All docs linked from Units 2, 3, 4, 5, and 6.
- [Filesystem MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) — the `npx -y @modelcontextprotocol/server-filesystem <root>` command.
- [Microsoft Learn — when to use agents vs workflows](https://learn.microsoft.com/en-us/agent-framework/overview/#when-to-use-agents-vs-workflows) — read this before scaling to multi-agent.
- The coding-agent shape (read/write/shell with approval gates, scoped to a sandbox) is our own design. Related inspirations worth studying: [Claude Code SDK](https://docs.claude.com/en/docs/claude-code/sdk), [Aider](https://aider.chat/), [MS GitHub Copilot SDK integration](https://learn.microsoft.com/en-us/agent-framework/agents/providers/github-copilot).
- See [`../SOURCES.md`](../SOURCES.md) for the full reference list.
