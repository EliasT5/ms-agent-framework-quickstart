# Unit 0 — Setup & sanity check

## What this is

The simplest possible Agent Framework program: ~10 lines of code that ask the model to say hello and print the response. No tools, no memory, no loop. Its only job is to confirm your environment is wired up.

## Why it matters

If this fails, nothing else in the curriculum will work. Debugging a broken hello-world is 10× easier than debugging a broken coding agent — so we isolate the "does the plumbing work?" question here.

## Mental model

At this point, an "agent" is just a thin wrapper around a chat completion call:

```
your prompt  →  [instructions + prompt]  →  OpenAI  →  response  →  you
```

The wrapper becomes meaningful later (tools, state, loops). For now, it's a polite hello.

## What the code does

1. Loads `.env` (your API key).
2. Creates an `OpenAIChatCompletionClient()` — reads `OPENAI_API_KEY` and `OPENAI_CHAT_COMPLETION_MODEL` from the environment.
3. Creates an agent with a one-line `instructions` string.
4. Runs the agent with `"Say hello in one short sentence."`
5. Prints the result.

Because Agent Framework is async, the call is wrapped in `asyncio.run(...)`.

## Try this

```powershell
python agent.py
```

Expected output:

```
Hello! How can I help you today?
```

(The exact wording varies — the model isn't deterministic.)

## Things to try next

- Change the instructions to `"You are Shakespeare. Respond in iambic pentameter."` and re-run. Feel how `instructions` shape the agent's voice.
- Change `OPENAI_CHAT_COMPLETION_MODEL` in `.env` to a different model your provider supports (e.g. `gpt-4o` instead of `gpt-4o-mini`) and re-run — notice how response quality and cost shift.

## When things break

- **`ModuleNotFoundError: agent_framework`** — venv isn't active, or `pip install -r requirements.txt` hasn't run.
- **`openai.AuthenticationError`** — key wrong or missing. Check `.env` has `OPENAI_API_KEY=sk-...` with no quotes, no spaces.
- **Nothing prints** — you probably forgot `asyncio.run()`. The agent returns a coroutine; you have to await it.
- **Windows `RuntimeError: Event loop is closed`** — harmless warning at shutdown on Windows; the script worked.

## Sources

- [Your First Agent — Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/get-started/your-first-agent) — the `pip install`, `load_dotenv()` note, and hello-world shape.
- [Sample `01_hello_agent.py`](https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/01_hello_agent.py) — our `agent.py` mirrors this.
- See [`../SOURCES.md`](../SOURCES.md) for the full reference list.
