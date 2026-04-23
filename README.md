# Microsoft Agent Framework — Hands-on Quickstart

A self-study curriculum that takes you from **zero to a working coding-agent prototype** in eight short units. Python SDK, v1.0 GA (April 2026). Runs on OpenAI — swapping providers is a one-line change.

## What is this framework, and why bother?

Microsoft Agent Framework is the direct successor to **Semantic Kernel** and **AutoGen**, built by the same teams. If you've heard of either, think of Agent Framework as "Semantic Kernel v2 fused with AutoGen's simple agent abstractions, plus graph-based workflows." It reached 1.0 in April 2026 with production-stable APIs.

It exists because Semantic Kernel had all the enterprise plumbing (state, middleware, telemetry) but clunky multi-agent ergonomics, and AutoGen had the clean agent loop but nothing for production. Agent Framework merges both and adds **MCP (Model Context Protocol)** support so you can plug in external tool collections the same way you install npm packages.

Useful if you're building on the Microsoft/Azure stack or want a production-stable agent SDK that speaks MCP natively.

## How this curriculum is structured

Eight units, each a self-contained folder with three files:

- **`README.md`** — the teacher voice. Read this first; it explains the concept in plain language with an analogy before any code.
- **`lesson.ipynb`** — an interactive notebook. Small cells, markdown between them, meant for tinkering. Change prompts, re-run, build intuition.
- **`agent.py`** — the same idea as a standalone script. `python agent.py` just works. This is what you'd actually ship.

Aim for ~20–30 minutes per unit. The first three are fast; Units 5 and 7 take longer because they involve external processes (MCP servers, shell commands).

## The curriculum

| # | Unit | What you'll learn |
|---|---|---|
| 0 | `unit-00-setup` | Install the framework, prove your API key works. ~5 min. |
| 1 | `unit-01-first-agent` | Create an agent with instructions; streaming vs. non-streaming. |
| 2 | `unit-02-tools` | Let the agent call your Python functions (the jump from chatbot to agent). |
| 3 | `unit-03-agentic-loops` ⭐ | The plan→act→observe→repeat loop. Watch it happen via middleware. |
| 4 | `unit-04-multi-turn` | Conversations that remember, using `AgentSession`. |
| 5 | `unit-05-mcp-plugins` ⭐ | Install pre-built tool collections: local (calculator) + remote (Microsoft Learn). |
| 6 | `unit-06-tool-approval` ⭐ | Human-in-the-loop gating: "may the agent send this email?" |
| 7 | `unit-07-coding-agent` ⭐ | Capstone: a real coding agent that reads, writes, and runs code — with approval. |

## One-time setup

See [`SETUP.md`](./SETUP.md). tl;dr: Python 3.10+, `python -m venv .venv`, activate, `pip install -r requirements.txt`, install `uv` for local MCP servers, run a local **LiteLLM proxy** on port 4000 (or point at your own OpenAI-compatible endpoint), and copy `.env.example` to `.env`.

## Running an example

```bash
.venv\Scripts\activate
python unit-00-setup\agent.py
```

Every unit's `agent.py` is independently runnable — no state carried between units. The notebooks are optional but recommended for Units 3, 5, 6, and 7 where you'll want to experiment.

## Out of scope

This is a quickstart, not a complete reference. Things you'll see hinted at but not explored:

- **Workflows** — graph-based multi-agent orchestration. Powerful, but a separate mental model. Pointers in Unit 7's "where to go next".
- **Azure Foundry / Entra auth** — the enterprise path. We use OpenAI because it's one env var. Switching providers is a one-line change (`OpenAIChatCompletionClient()` → `AzureOpenAIChatClient(...)` or `FoundryChatClient(...)`).
- **Hosting** (Azure Functions, A2A) — deploying an agent is its own topic.
- **Observability** (OpenTelemetry, tool-level tracing) — production next step.
- **Hardened sandboxing** for the coding agent in Unit 7 — we use approval + a scoped folder. Real deployments should containerize shell execution.

## Troubleshooting

Most problems are env setup. If `unit-00-setup/agent.py` doesn't print a greeting, don't move on — fix the environment first. Each unit's README has a "when things break" section at the bottom.

## Verify everything

See [`SOURCES.md`](./SOURCES.md) for a per-unit list of the official Microsoft docs each lesson is based on. Every claim, API spelling, and code pattern in this curriculum is traceable to a specific page on [learn.microsoft.com](https://learn.microsoft.com/en-us/agent-framework/) or a sample file in the [`microsoft/agent-framework`](https://github.com/microsoft/agent-framework) repo. If a lesson contradicts the linked doc, trust the doc.

## Top-level sources

- [Microsoft Learn — Agent Framework](https://learn.microsoft.com/en-us/agent-framework/)
- [GitHub — microsoft/agent-framework](https://github.com/microsoft/agent-framework)
- [PyPI — agent-framework](https://pypi.org/project/agent-framework/)
- [Python samples folder](https://github.com/microsoft/agent-framework/tree/main/python/samples)
