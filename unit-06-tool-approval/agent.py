"""
Unit 6 — Tool approval (human-in-the-loop).

Goal: two tools on one agent. One runs freely; the other requires
human approval. Shows the approval loop pattern using a session so
the agent has full history across approval rounds.

Run: python agent.py
"""

import asyncio
from random import randint
from typing import Annotated, Any

from agent_framework import AgentResponse, Message, tool
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()


@tool(approval_mode="never_require")
def get_weather(
    city: Annotated[str, Field(description="The city to check, e.g. 'Vienna'.")],
) -> str:
    """Return the current weather for a city."""
    conditions = ["sunny", "cloudy", "overcast"]
    return f"{city}: {conditions[randint(0, 2)]}, {randint(10, 25)}°C"


@tool(approval_mode="always_require")
def send_email(
    to: Annotated[str, Field(description="Recipient email address.")],
    subject: Annotated[str, Field(description="Email subject line.")],
    body: Annotated[str, Field(description="Email body text.")],
) -> str:
    """Send an email to a recipient. Requires user approval before sending."""
    print(f"\n    [fake-mailer] to={to!r}\n                 subject={subject!r}\n                 body={body!r}\n")
    return f"email sent to {to}"


async def handle_approvals(query: str, agent, session, max_rounds: int = 10) -> AgentResponse:
    """Run the agent, handling approval requests by prompting the user.

    The session carries the full conversation (user query, the agent's
    tool calls and approval requests, and our approval responses) across
    rounds — we only need to feed it the new approval responses each time.
    """
    result = await agent.run(query, session=session)

    rounds = 0
    while result.user_input_requests:
        rounds += 1
        if rounds > max_rounds:
            raise RuntimeError(
                f"Exceeded {max_rounds} approval rounds — likely the provider "
                "isn't honoring approval responses. Check your LiteLLM/provider setup."
            )

        # Collect user decisions. Each approval response is a user-role Message
        # containing the to_function_approval_response Content.
        responses: list[Any] = []
        for request in result.user_input_requests:
            fn = request.function_call
            print(f"\n  Approval requested:")
            print(f"    function: {fn.name}")
            print(f"    args:     {fn.arguments}")
            answer = await asyncio.to_thread(input, "  Approve? (y/n): ")
            approved = answer.strip().lower().startswith("y")
            responses.append(
                Message("user", [request.to_function_approval_response(approved)])
            )

        # Re-run with the session so the agent sees the prior approval request
        # AND our response. Without a session the agent would replan from
        # scratch and ask again forever.
        result = await agent.run(responses, session=session)

    return result


async def main() -> None:
    agent = OpenAIChatCompletionClient().as_agent(
        name="Picnicker",
        instructions=(
            "You help plan picnics and send update emails. "
            "Check the weather before composing any email. Keep emails short and cheerful."
        ),
        tools=[get_weather, send_email],
    )

    session = agent.create_session()

    prompt = (
        "Email alex@example.com that the weather in Vienna looks great for the picnic. "
        "Check the weather first and include the forecast in the email."
    )
    print(f"User: {prompt}\n")
    print("(get_weather runs silently; send_email will ask for approval)")

    result = await handle_approvals(prompt, agent, session)
    print(f"\nAgent: {result.text}")


if __name__ == "__main__":
    asyncio.run(main())
