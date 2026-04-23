"""
Unit 4 — Multi-turn conversations with AgentSession.

Goal: demonstrate stateless-without-session vs. stateful-with-session,
then drop into an interactive REPL you can chat with.

Run: python agent.py
"""

import asyncio
from typing import Annotated

from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()


def get_weather(
    city: Annotated[str, Field(description="City name, e.g. 'Berlin'.")],
) -> str:
    """Return the current weather for a city."""
    faked = {
        "berlin": "12°C, overcast",
        "vienna": "15°C, sunny",
        "munich": "10°C, light rain",
        "paris": "14°C, clear",
    }
    return faked.get(city.lower(), f"{city}: weather data unavailable")


async def forgetful_demo(agent) -> None:
    """Same agent, no session. The agent forgets between calls."""
    print("--- Forgetful demo (no session) ---")
    r1 = await agent.run("What's the weather in Berlin?")
    print("User: What's the weather in Berlin?")
    print(f"1. {r1.text}")
    r2 = await agent.run("What was the city I just asked about?")
    print("What was the city I just asked about?")
    print(f"2. {r2.text}")
    print()


async def repl(agent) -> None:
    """Chat with the agent across turns, sharing a session."""
    print("--- Chat (with session) ---")
    print("Type messages, 'quit' to exit.\n")

    session = agent.create_session()

    while True:
        try:
            user = await asyncio.to_thread(input, "> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user.strip():
            continue
        if user.strip().lower() in {"quit", "exit", "bye"}:
            print("bye.")
            break

        result = await agent.run(user, session=session)
        print(f"< {result.text}\n")


async def main() -> None:
    agent = OpenAIChatCompletionClient().as_agent(
        name="ChatAgent",
        instructions=(
            "You are a helpful, concise assistant. "
            "Use the weather tool when a user asks about conditions in a city. "
            "Refer back to earlier turns when relevant."
        ),
        tools=[get_weather],
    )

    await forgetful_demo(agent)
    await repl(agent)


if __name__ == "__main__":
    asyncio.run(main())
