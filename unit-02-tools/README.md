# Unit 2 — Custom function tools

## What this is

The step that turns a chatbot into an agent. You write ordinary Python functions. You pass them to the agent. The agent decides when to call them.

## Why it matters

A raw LLM can only manipulate text. It can't check today's weather, query your database, or write a file. Tools are how you extend the LLM into the real world — and they're the building block for everything that follows: agentic loops (Unit 3), MCP plugins (Unit 5 — same concept, distributed), approval gates (Unit 6), the coding agent (Unit 7).

## Mental model

**The agent decides. You never call tools yourself.**

When you give an agent a function, the SDK:

1. Inspects the function signature and docstring, turns it into a JSON schema.
2. Sends that schema to the model along with your prompt.
3. If the model decides to use the tool, the SDK calls your Python function for it, captures the return value, and hands it back to the model.
4. The model composes a final answer using the tool's output.

From your code's point of view, you only ever call `agent.run(prompt)`. The tool-calling is invisible plumbing — but see Unit 3 for how to make it visible.

## What the code does

- Defines two plain Python functions: `get_weather(city)` and `get_time(timezone)`. The return values are fake (hardcoded strings) — that's fine; real tools talk to real APIs, but for learning the *shape* is what matters.
- Uses `Annotated[str, Field(description="...")]` to document each parameter. **This matters** — the model only sees what you annotate, so good descriptions = good tool use.
- Passes `tools=[get_weather, get_time]` to `client.as_agent(...)`.
- Asks: *"What's the weather in Berlin and what time is it there?"* The agent calls both tools, then composes one answer.

## Try this

```powershell
python agent.py
```

You should see an answer that combines the weather fact and the time fact into one sentence. You never saw the tool calls happen — they're hidden. (Unit 3 will fix that.)

## Things to try next

- Ask a question that needs neither tool (`"Tell me a joke"`) — the agent won't call them.
- Ask something ambiguous (`"What's it like in Munich?"`) — the agent usually picks the weather tool.
- Break a tool's description: change `"The city to look up"` to `"Input"` and watch the agent struggle to use it correctly. Good docs matter.
- Add a third tool: `get_population(city: str) -> str`. Re-run with `"How big is Paris, what's the weather, and what time is it?"`.

## Why `Annotated[type, Field(description=...)]`?

Python's built-in type hints tell the model *what type* a parameter is. The `Field(description=...)` from Pydantic tells it *what the parameter means*. Both get serialized into the JSON schema the model sees. Without the description, the model has to guess from the parameter name alone — often wrong.

## When things break

- **Agent ignores your tool** — description is unclear, or the tool's docstring doesn't explain *when* to use it. Be explicit: `"""Use this to look up the current weather for a city."""`
- **Agent hallucinates a tool call with wrong arguments** — you used an untyped parameter (`city` instead of `city: str`).
- **Tool gets called but returns wrong data** — that's your code's problem; agents can only use what you return.

## Sources

- [Tools Overview](https://learn.microsoft.com/en-us/agent-framework/agents/tools/) — full tool-type matrix and provider support.
- [Function Tools](https://learn.microsoft.com/en-us/agent-framework/agents/tools/function-tools) — the `Annotated[type, Field(description=...)]` pattern.
- [Sample `02_add_tools.py`](https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/02_add_tools.py)
- See [`../SOURCES.md`](../SOURCES.md) for the full reference list.
