# Unit 4 — Multi-turn conversations with `AgentSession`

## What this is

Make the agent remember what you said. You'll build a REPL (read-eval-print loop) where each turn of the conversation feeds back into the next.

## Why it matters

Without memory, every `agent.run()` is a fresh start. The agent has no idea who you are, what you asked before, or what it told you. That's fine for one-shot calls but ruinous for assistants. Unit 7's coding agent uses a session so you can say "now add tests" after it writes `fizz.py`, and it knows *which* tests.

## Mental model

**Agents are stateless. Sessions are stateful.**

An `AgentSession` is a container for the conversation transcript. You create one with `agent.create_session()`, pass it into every `agent.run(..., session=session)` call, and the framework replays the stored messages into the model each turn. The session silently grows as you go.

That's it — no magic memory, no learned knowledge, just a growing transcript.

Two consequences:

1. **It grows forever.** Every turn adds tokens. Eventually you hit context limits. In production you'd truncate or summarize older messages. For ~20 turns you're fine.
2. **It resets on process restart.** Sessions are in-memory by default. For persistence, serialize them (`session.to_dict()` / `AgentSession.from_dict(...)`) and store that yourself.

## What the code does

1. Creates a tool-enabled agent (reusing the weather pattern from Unit 2).
2. Shows a **forgetful demo** first — same agent, two separate `.run()` calls with no session — so you feel the baseline.
3. Creates an `AgentSession` via `agent.create_session()`.
4. Runs a REPL: read stdin, `agent.run(user, session=session)`, print, loop.

## Try this

```powershell
python agent.py
```

First you'll see the forgetful demo. Then the REPL starts. Try:

```
> What's the weather in Berlin?
< Berlin: 12°C, overcast.
> And in Munich?
< Munich: 10°C, light rain.       ← it understood "And in" refers to weather
> What was the first city I asked about?
< Berlin.                         ← it remembers
> quit
```

Ctrl+C or type `quit` to exit.

## Things to try next

- Remove `session=session` from the REPL's `.run()` call and re-run. The agent forgets every turn.
- Inspect `session.to_dict()` after a few turns to see the raw transcript.
- Combine a session + the middleware from Unit 3. Memory + tool-call visibility = the shape of the Unit 7 coding agent.

## When things break

- **`AttributeError: 'Agent' object has no attribute 'create_session'`** — framework version skew. Make sure `pip install -U agent-framework` is recent (≥ 1.1).
- **Agent ignores earlier turns** — you forgot to pass `session=session` to one of the `.run()` calls.
- **Context length exceeded after many turns** — transcript got too big. Restart the REPL or summarize.

## Sources

- [Step 3: Multi-Turn Conversations](https://learn.microsoft.com/en-us/agent-framework/get-started/multi-turn) — the `session = agent.create_session()` + `agent.run(..., session=session)` pattern.
- [`AgentSession` API reference](https://learn.microsoft.com/en-us/python/api/agent-framework-core/)
- [Multi-turn tutorial](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/multi-turn-conversation)
- See [`../SOURCES.md`](../SOURCES.md) for the full reference list.
