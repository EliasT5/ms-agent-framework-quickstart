# Unit 5 — Installing MCP plugins & skills ⭐

## What this is

Give your agent capabilities you didn't write. You'll "install" two plugins:

- **Part A (local):** a calculator that runs as a subprocess on your machine (stdio-based MCP).
- **Part B (remote):** Microsoft's own MCP server at `learn.microsoft.com/api/mcp` that lets the agent search real Microsoft documentation.

Then you'll combine both on one agent and watch it pick the right tool for the job.

## Why it matters

MCP — **Model Context Protocol** — is to agents what npm is to Node or apt is to Linux. It's the open standard (adopted by Microsoft, Anthropic, OpenAI, and everyone else in 2025) for distributing reusable agent tool collections.

Once you can install plugins, your agent isn't limited to what you wrote. Anyone in the world can publish a skill; you can consume it with two lines of code. This is the feature that makes Agent Framework production-viable — you'll never re-implement "search GitHub" or "query SQLite" yourself.

## Mental model

An **MCP server** is just a program that speaks a particular JSON-RPC-over-whatever protocol. It exposes a list of tools, and it knows how to execute them. You don't care about the protocol — Agent Framework does the translation.

Three ways a server can run:

| Type | How it runs | When to use |
|---|---|---|
| **stdio** (`MCPStdioTool`) | Local process, you give the command | Local tools (calculator, filesystem, SQLite) |
| **HTTP** (`MCPStreamableHTTPTool`) | Remote URL | Cloud-hosted services (MS Learn, company APIs) |
| **WebSocket** (`MCPWebsocketTool`) | Persistent socket | Real-time data streams |

You attach them the same way you attach a Python function: `tools=[my_mcp_tool]` on the agent. The framework calls `.list_tools()` on the server, hands that schema to the model, and when the model wants to use a tool the framework round-trips through the server.

## Part A — local plugin (stdio): calculator

```python
async with MCPStdioTool(
    name="calculator",
    command="uvx",
    args=["mcp-server-calculator"],
) as calc_tool:
    agent = OpenAIChatCompletionClient().as_agent(..., tools=[calc_tool])
```

`uvx` downloads and runs `mcp-server-calculator` from PyPI in an ephemeral environment, no permanent install. First run takes ~10 seconds (download); subsequent runs are instant.

We prompt the agent with `"What is 23 * 47 + 113?"`. Without the calculator plugin, the model guesses arithmetic (and often gets it wrong for non-trivial math). With it, the agent calls the calculator tool and returns the exact answer.

## Part B — remote plugin (HTTP): Microsoft Learn

```python
async with MCPStreamableHTTPTool(
    name="ms-learn",
    url="https://learn.microsoft.com/api/mcp",
) as learn_tool:
    agent = OpenAIChatCompletionClient().as_agent(..., tools=[learn_tool])
```

No install, no server to run — it's just a URL. We ask `"How do I create an Azure storage account with the az CLI?"` and the agent queries real Microsoft docs and composes an answer grounded in them. Compared to the raw LLM's answer (which might be outdated or hallucinated), this one cites actual documentation.

## Part C — combine + watch

Both MCP plugins + a plain Python `save_note()` tool, all on one agent, with Unit 3's logging middleware attached. You ask a compound question and watch the agent route to the right tool each time:

- *"What's 500 * 23?"* → calls the calculator
- *"How do I deploy an Azure Function?"* → calls MS Learn
- *"Save that as a note titled 'azure-func-steps'"* → calls `save_note`

## What the code does

`agent.py` runs Part A, then Part B, then Part C — each as a separate `async` function. You get three blocks of output.

## Try this

```powershell
python agent.py
```

On first run, Part A may hang for ~10 seconds while `uvx` downloads the calculator server. If it hangs longer, check your network.

## Things to try next (other popular MCP plugins)

Swap the calculator line for any of these:

- **Filesystem:** `command="npx", args=["-y", "@modelcontextprotocol/server-filesystem", "./some-folder"]` — read/list/grep files (used in Unit 7).
- **SQLite:** `command="uvx", args=["mcp-server-sqlite", "--db-path", "my.db"]` — query a database.
- **Fetch:** `command="uvx", args=["mcp-server-fetch"]` — let the agent fetch arbitrary URLs.
- **GitHub:** `command="npx", args=["-y", "@modelcontextprotocol/server-github"]` — read repos, file issues, etc. (needs `GITHUB_TOKEN`).
- **Brave Search:** `command="npx", args=["-y", "@modelcontextprotocol/server-brave-search"]` — web search (needs API key).

Browse the [official MCP server registry](https://github.com/modelcontextprotocol/servers) for more. The pattern is always the same.

## When things break

- **`FileNotFoundError: uvx`** — you skipped step 6 in SETUP.md. `pip install uv`.
- **First-run hang >30s** — `uvx` is downloading. Check network, or pre-install with `uv tool install mcp-server-calculator`.
- **`TimeoutError` on MS Learn** — Microsoft's MCP endpoint occasionally returns 503. Retry; if persistent, use Part A only.
- **MCP tool doesn't fire** — make sure you `await` the `async with` block correctly; the tool only exists inside the context.

## Sources

- [Using MCP Tools — Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools) — the canonical reference for `MCPStdioTool`, `MCPStreamableHTTPTool`, `MCPWebsocketTool`. Both the calculator example (stdio) and the Microsoft Learn example (HTTP) come directly from this page.
- [MCP (Model Context Protocol) homepage](https://modelcontextprotocol.io/)
- [Public MCP server registry](https://github.com/modelcontextprotocol/servers) — calculator, filesystem, GitHub, SQLite, etc.
- See [`../SOURCES.md`](../SOURCES.md) for the full reference list.
