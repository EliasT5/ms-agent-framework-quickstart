# Sources & Verification

Every claim and API usage in this curriculum can be traced back to official Microsoft documentation or the `microsoft/agent-framework` GitHub repo. Use this file to verify the code — if something in a lesson doesn't match the linked doc, the doc is right and I got it wrong.

**Framework version when written:** Agent Framework 1.0 GA (Python), April 2026.

## Master references

| Resource | Purpose |
|---|---|
| [Agent Framework docs — landing](https://learn.microsoft.com/en-us/agent-framework/) | Official Microsoft Learn index |
| [`microsoft/agent-framework` on GitHub](https://github.com/microsoft/agent-framework) | Source code, samples, issues |
| [`agent-framework` on PyPI](https://pypi.org/project/agent-framework/) | Python package |
| [Python API reference](https://learn.microsoft.com/en-us/python/api/agent-framework-core/) | Class-level reference for every public symbol |
| [Python samples folder](https://github.com/microsoft/agent-framework/tree/main/python/samples) | Canonical runnable examples |
| [1.0 release announcement](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/) | What GA means; API stability promises |
| [MCP (Model Context Protocol) spec](https://modelcontextprotocol.io/) | The open plugin standard |
| [MCP server registry](https://github.com/modelcontextprotocol/servers) | Public plugins you can install |

## Unit-by-unit sources

### Unit 0 — Setup
- [Your First Agent (official tutorial)](https://learn.microsoft.com/en-us/agent-framework/get-started/your-first-agent) — the `pip install agent-framework`, `.env` note, and the 10-line hello-world pattern come straight from here.
- [Sample: `01_hello_agent.py`](https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/01_hello_agent.py) — our `agent.py` mirrors this.

### Unit 1 — First agent (streaming vs non-streaming)
- [Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/) — covers `run()` and `run(stream=True)`.
- [Sample: `01_hello_agent.py`](https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/01_hello_agent.py) — shows both modes side by side, same as our lesson.

### Unit 2 — Custom function tools
- [Tools Overview](https://learn.microsoft.com/en-us/agent-framework/agents/tools/) — tool-type matrix and provider support.
- [Function Tools](https://learn.microsoft.com/en-us/agent-framework/agents/tools/function-tools) — the `Annotated[type, Field(description=...)]` pattern.
- [Sample: `02_add_tools.py`](https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/02_add_tools.py)

### Unit 3 — Agentic loops (middleware)
- [Agent Middleware](https://learn.microsoft.com/en-us/agent-framework/agents/middleware/) — `function_middleware`, `FunctionInvocationContext`, `context.function.name`, `context.arguments`, `context.result`.
- [AutoGen → Agent Framework migration](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) — the "no `max_tool_iterations`" claim. Search for "automatic" on that page; the migration guide explicitly says Agent Framework iterates until completion by default with built-in safeguards.

### Unit 4 — Multi-turn (`AgentSession`)
- [Step 3: Multi-Turn Conversations](https://learn.microsoft.com/en-us/agent-framework/get-started/multi-turn) — the `session = agent.create_session()` + `agent.run(..., session=session)` pattern. (Note: some older docs still say `AgentThread` / `get_new_thread()` — the installed 1.1 API renamed these to `AgentSession` / `create_session()`.)
- [`AgentSession` API reference](https://learn.microsoft.com/en-us/python/api/agent-framework-core/)
- [Multi-turn tutorial (with ChatMessageStore)](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/multi-turn-conversation)
- [Sample: `03_multi_turn.py`](https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/03_multi_turn.py)

### Unit 5 — MCP plugins & skills
- [Using MCP Tools](https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools) — `MCPStdioTool`, `MCPStreamableHTTPTool`, `MCPWebsocketTool`. Both the calculator stdio example and the Microsoft Learn HTTP example come from this page.
- [MCP protocol homepage](https://modelcontextprotocol.io/)
- [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) — the public plugin registry. Our examples (`mcp-server-calculator`, `@modelcontextprotocol/server-filesystem`) are both listed there.
- [Microsoft Learn MCP endpoint reference](https://learn.microsoft.com/en-us/training/support/microsoft-learn-mcp-faq) — confirms the public URL `https://learn.microsoft.com/api/mcp`.

### Unit 6 — Tool approval
- [Using function tools with human-in-the-loop approvals](https://learn.microsoft.com/en-us/agent-framework/agents/tools/tool-approval) — `@tool(approval_mode="always_require")`, `result.user_input_requests`, `request.to_function_approval_response(bool)`, the `Message("assistant", [...])` / `Message("user", [...])` approval-loop pattern. Our `handle_approvals` function is a faithful translation of the "complete example" near the bottom of that page.
- [Tool approval provider support matrix](https://learn.microsoft.com/en-us/agent-framework/agents/tools/) — confirms approval works with the Chat Completion client (what we use with `OpenAIChatCompletionClient`), contrary to what you might guess from older AutoGen docs.

### Unit 7 — Capstone coding agent
Everything from Units 2, 3, 4, 5, and 6, plus:
- [Filesystem MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) — the `npx -y @modelcontextprotocol/server-filesystem <root>` invocation.
- The coding-agent shape (read/write/shell with approval gates, scoped to a workspace) is our own synthesis. Inspiration: [Claude Code SDK](https://docs.claude.com/en/docs/claude-code/sdk), [Aider](https://aider.chat/), and MS's own [GitHub Copilot SDK integration](https://learn.microsoft.com/en-us/agent-framework/agents/providers/github-copilot) — but the curriculum code doesn't depend on any of those.

## API symbols used (verified spellings)

Every `from agent_framework ...` or `from agent_framework.openai ...` import in this curriculum matches the current 1.0 public API. If you get `ImportError`, upgrade (`pip install -U agent-framework`) — old pre-1.0 betas had different names.

| Symbol | Import path | Used in |
|---|---|---|
| `OpenAIChatCompletionClient` | `agent_framework.openai` | Units 0–7 |
| `tool` decorator | `agent_framework` | Units 6, 7 |
| `Agent` / `client.as_agent()` | `agent_framework` / client method | Units 0–7 |
| `agent.run(msg, stream=True)` | instance method (streaming) | Unit 1 |
| `AgentResponse` | `agent_framework` | Units 6, 7 |
| `Message` | `agent_framework` | Units 6, 7 |
| `function_middleware` | `agent_framework` | Units 3, 5, 7 |
| `FunctionInvocationContext` | `agent_framework` | Units 3, 5, 7 |
| `MCPStdioTool` | `agent_framework` | Units 5, 7 |
| `MCPStreamableHTTPTool` | `agent_framework` | Unit 5 |
| `agent.create_session()` / `AgentSession` | instance method / class | Units 4, 5, 7 |
| `result.user_input_requests` | response attribute | Units 6, 7 |
| `request.to_function_approval_response(bool)` | method | Units 6, 7 |

## If something is wrong

Open an issue on this repo. If it's the framework's fault, file on [microsoft/agent-framework](https://github.com/microsoft/agent-framework/issues). If it's mine, I'll fix it.
