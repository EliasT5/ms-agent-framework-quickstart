# Unit 6 — Tool approval (human-in-the-loop) ⭐

## What this is

Some tools are cheap and safe — looking up the weather, doing arithmetic. Others are not: sending an email, deleting a file, charging a credit card. For the dangerous ones you want the agent to **ask first**.

Agent Framework has a decorator for exactly that: `@tool(approval_mode="always_require")`. When the agent decides to call that tool, the framework pauses, hands control back to you, and waits for a yes/no.

## Why it matters

This is the guardrail that makes agents safe to deploy. Especially for Unit 7 — a coding agent that can run shell commands needs approval gates or it will eventually `rm -rf` something you care about. You'll see the exact same `@tool(approval_mode="always_require")` pattern on `write_file` and `run_shell` there.

## Mental model

Without approval, the loop is:

```
prompt → model calls tool → tool runs → model uses result → answer
```

With approval, it becomes:

```
prompt → model WANTS to call tool → pause, ask human → {yes: run it, no: tell the model}
         → model uses result (or apology) → answer
```

The pause happens inside `agent.run()`. When the agent returns, you check `result.user_input_requests`. If that list is non-empty, the agent has paused and is asking you to decide. You:

1. Look at each `user_input_needed.function_call.name` and `.arguments`.
2. Ask the human (or your UI) yes/no.
3. Build an approval response with `user_input_needed.to_function_approval_response(True)` (or `False`).
4. Call `agent.run([approval_response], session=session)` — **with the same session** you used on the first call.
5. The agent resumes where it left off. If there are more approvals pending, repeat.

**Why the session matters.** Without `session=session`, each `agent.run()` starts from a blank slate. The agent doesn't know it already tried to call `send_email`, re-plans the whole task, lands on `send_email` again, and asks for approval a second time — forever, regardless of your y/n. Using a session ties the approval response to the pending tool call so the agent resumes instead of restarting.

This is called the **approval loop** and the code shows it as a reusable function.

## The two approval modes

| Mode | Behavior |
|---|---|
| `"never_require"` | Default — agent runs the tool without asking. |
| `"always_require"` | Agent pauses on every call. Use for dangerous tools. |

You set it once on the tool, not per-call. (Older docs mention a `"require_once"` mode — not present in the 1.1 API. To only ask once per session, track approved function+args in your own approval loop.)

## What the code does

- Defines two tools on one agent:
  - `get_weather(city)` — normal `@tool`, no approval needed.
  - `send_email(to, subject, body)` — `@tool(approval_mode="always_require")`.
- Asks: *"Email alex@example.com that the weather in Vienna looks great for the picnic. Check the weather first."*
- Watch: `get_weather` is called freely (no prompt). Then the agent tries to call `send_email` and pauses.
- Terminal prints the full call details and asks you `y/n`.
- If you say `y`, the "email" is "sent" (our fake implementation just prints it) and the agent confirms.
- If you say `n`, the agent reports that it couldn't complete the request.

## Try this

```powershell
python agent.py
```

Expected:

```
User: Email alex@example.com that the weather in Vienna looks great for the picnic.

(agent calls get_weather silently)

Approval requested:
  function: send_email
  args: {'to': 'alex@example.com', 'subject': 'Picnic update', 'body': '...'}
Approve? (y/n): y

Agent: Email sent. Vienna looks sunny at 15°C - perfect picnic conditions.
```

Try running it again and typing `n`. Watch the agent gracefully tell you it couldn't complete.

## Things to try next

- Modify `handle_approvals` to remember approved function+args within the session (`{(name, frozenset(args.items()))}`) and auto-approve repeats. Now your user is only asked once per unique call.
- Add a third tool `delete_all_emails()` with `approval_mode="always_require"`. Now you have two approval-gated tools. The loop handles both.
- In a real app, `asyncio.to_thread(input, ...)` becomes a call to your UI/Slack/webhook. Same logic, different source.

## When things break

- **Agent calls the "dangerous" tool without asking** — you forgot the parentheses on the decorator (`@tool` vs `@tool(approval_mode="always_require")`), or the mode is wrong.
- **Infinite approval loop** — you forgot `session=session`. The loop in this unit uses a session precisely so each re-run resumes from the pending call rather than replanning. The script has a safety `max_rounds` cap that raises if the loop exceeds 10 rounds.
- **`AttributeError: '...' object has no attribute 'to_function_approval_response'`** — older package version. Newer APIs expose `.create_response(bool)` with the same effect; adjust if needed.

## Sources

- [Using function tools with human-in-the-loop approvals](https://learn.microsoft.com/en-us/agent-framework/agents/tools/tool-approval) — the canonical reference. Our `handle_approvals` function is a faithful translation of the "complete example" near the bottom of that page: `approval_mode="always_require"`, `result.user_input_requests`, `request.to_function_approval_response(bool)`, and the `Message("assistant", [...])` / `Message("user", [...])` loop.
- [Tool approval provider matrix](https://learn.microsoft.com/en-us/agent-framework/agents/tools/) — confirms this works with `OpenAIChatCompletionClient` (Chat Completion).
- See [`../SOURCES.md`](../SOURCES.md) for the full reference list.
