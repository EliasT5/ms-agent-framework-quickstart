# Unit 1 — Your first (real) agent

## What this is

Two ways to run an agent — **non-streaming** (wait for the whole response, then print) and **streaming** (print each chunk of text as it arrives). Same agent, same prompt. You'll feel the difference immediately.

## Why it matters

- **Non-streaming** is what you use when another piece of code consumes the output (you need the full string before you can do anything with it).
- **Streaming** is what you use when a human is watching. It's the reason ChatGPT feels fast — the first word appears in under a second, even if the full answer takes 10.

You'll use both, often in the same app, depending on where the output is going.

## Mental model

Think of `instructions` as **personality baked in**. The agent is set up once with "You are a terse pirate" — every run after that speaks like a pirate without you repeating yourself.

- `agent.run(prompt)` → mail-order response. You get the whole thing at once.
- `agent.run(prompt, stream=True)` → watching someone type. Chunks arrive as they're generated.

Under the hood they're the same LLM call; the difference is whether the SDK buffers the response or yields tokens as they come.

## What the code does

1. Creates one agent with pirate instructions.
2. Asks it the same question twice: once with `run()`, once with `run(stream=True)`.
3. For the stream, iterates over chunks and prints each one as it arrives (with `end=""` and `flush=True` so it shows up immediately).

## Try this

```powershell
python agent.py
```

You'll first see the non-streaming response print instantly as a complete block. Then the streaming response will type itself out word by word.

## Things to try next

- Shorten the instructions to just `"You are a pirate."` — the agent rambles more.
- Ask a longer question like `"Explain quantum entanglement in the style of a pirate."` to really feel the streaming difference.
- In a chat UI you'd pipe the stream chunks to a WebSocket / SSE channel instead of `print()`. Same loop, different destination.

## When things break

- **Nothing streams, it all appears at once** — you forgot `flush=True` on `print`, or your terminal is buffering. Try `sys.stdout.flush()` after each chunk.
- **`AttributeError: 'coroutine' object has no attribute '__aiter__'`** — you wrote `for chunk in agent.run(..., stream=True)` instead of `async for chunk in agent.run(..., stream=True)`.

## Sources

- [Your First Agent — Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/get-started/your-first-agent) — shows non-streaming and streaming side by side, same pattern as this unit.
- [Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/)
- See [`../SOURCES.md`](../SOURCES.md) for the full reference list.
