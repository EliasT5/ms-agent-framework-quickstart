# Unit 3 — Agentic loops ⭐

## What this is

The core pattern that makes agents *agentic*: **plan → act → observe → repeat**. The model looks at a task, decides to call a tool, reads the result, decides whether to call another tool, and so on — until it has enough to answer.

You don't write this loop. It happens inside `agent.run()`. Your job is to give the agent good tools and a good task.

## Why it matters

The difference between Unit 2 (one tool call) and this unit (four tool calls, chained) is the difference between a smart chatbot and a real agent. Once you've seen the loop happen and watched it through middleware, everything else in this curriculum is variations on the theme.

## How it works in Microsoft Agent Framework

**It's automatic.** In AutoGen you'd have set `max_tool_iterations=5`. Here you don't — `Agent.run()` iterates until the model returns a text answer instead of another tool call, with internal safeguards against runaway loops.

This is a deliberate design choice. Microsoft's team looked at AutoGen's explicit loop count, decided it was leaky abstraction (why should you know the number?), and built the safeguards in. You focus on tools + instructions; the loop takes care of itself.

## Mental model

A conversation the agent has with itself:

```
Model: "User wants a picnic plan for Vienna tomorrow. I need the weather."
       calls get_weather("Vienna", "tomorrow") → "18°C, partly sunny"
Model: "Good. Now the hourly forecast."
       calls get_forecast_hourly("Vienna") → "morning showers, clear afternoon"
Model: "So: afternoon. What parks are nearby?"
       calls find_parks("Vienna") → ["Stadtpark", "Prater", "Augarten"]
Model: "Prater is best for a group. What food fits 18°C sunny?"
       calls suggest_food("sunny 18°C") → "light salads, cold drinks"
Model: done — compose answer.
```

Each step is a round-trip to the model. Each round-trip is one API call. **Multi-step tasks aren't free** — they cost more tokens and time than single-step ones. That's why Unit 7 tells the coding agent to "read before writing": reading is cheap, writing is expensive, and the agent should plan accordingly.

## Watching the loop: middleware

By default the loop is invisible. You see input, you see output, the middle is a black box. **Function middleware** lets you hook in between: the SDK calls your middleware before it calls each tool, and again after. You just print.

The middleware we use here is a function decorated with `@function_middleware`:

```python
@function_middleware
async def log_tool_calls(context, call_next):
    print(f"[→] {context.function.name}({context.arguments})")
    await call_next()
    print(f"[←] {context.function.name} → {context.result!r}")
```

`context.function.name` is the tool's name. `context.arguments` is the kwargs dict the model chose. `await call_next()` actually runs the tool (or the next middleware in the chain). After it, `context.result` holds the return value.

Attach it via `middleware=[log_tool_calls]` on the agent.

## What the code does

1. Defines four tools (weather, hourly forecast, parks, food suggestions). All fake-data, all small.
2. Defines a `log_tool_calls` middleware that prints each call in/out.
3. Creates an agent with all four tools plus the middleware.
4. Asks: *"Plan a picnic for tomorrow in Vienna. Tell me the time of day, where to go, and what to bring."*
5. You watch three or four tool calls scroll past, then the final plan.

## Try this

```powershell
python agent.py
```

Expected (abbreviated):

```
User: Plan a picnic for tomorrow in Vienna. ...

[→] get_weather({'city': 'Vienna', 'date': 'tomorrow'})
[←] get_weather → '18°C, partly sunny'
[→] get_forecast_hourly({'city': 'Vienna'})
[←] get_forecast_hourly → 'morning showers, clear afternoon'
[→] find_parks({'city': 'Vienna'})
[←] find_parks → 'Stadtpark, Prater, Augarten'
[→] suggest_food({'weather': 'sunny, 18°C'})
[←] suggest_food → 'light salads, cold drinks'

Agent: Tomorrow afternoon looks perfect for a Vienna picnic. Head to Prater...
```

The exact sequence will vary. Sometimes the model figures it out in three calls. Sometimes five. You didn't decide; it did.

## Things to try next

- Remove one of the tools. The agent will work around the gap, or tell you it can't answer.
- Add an intentional failure: make `get_weather` return `"error: API down"`. The agent should handle it gracefully and maybe try without weather info.
- Make the instructions stricter: `"Always check weather first, then forecast, then parks, then food."` Now the order is pinned — but so is the rigidity. Agentic = flexible; scripted = predictable. Trade-offs.

## When things break

- **The agent answers without calling any tools** — tools' docstrings are too vague; the model doesn't see the need. Be explicit about *when* to use each.
- **The loop runs 10+ calls** — the agent is confused. Usually means tool descriptions overlap or the task is ambiguous. Simplify the task.
- **Middleware doesn't fire** — make sure you passed it via `middleware=[log_tool_calls]` on `client.as_agent(...)`, not just defined it.

## Sources

- [Agent Middleware](https://learn.microsoft.com/en-us/agent-framework/agents/middleware/) — the three middleware types (agent / function / chat), `FunctionInvocationContext`, `context.function.name`, `context.arguments`, `context.result`, and the `@function_middleware` decorator.
- [AutoGen → Agent Framework Migration](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) — explicitly covers "Agent Framework handles tool iteration automatically at the agent level" (search for "automatic") — the reason we don't set `max_iterations`.
- See [`../SOURCES.md`](../SOURCES.md) for the full reference list.
