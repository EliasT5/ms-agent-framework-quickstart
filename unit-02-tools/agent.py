"""
Unit 2 — Custom function tools.

Goal: give the agent two Python functions and watch it decide when
to call them to answer a compound question.

Run: python agent.py
"""

import asyncio
from datetime import datetime
from typing import Annotated

from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()


def get_weather(
    city: Annotated[str, Field(description="The city to look up, e.g. 'Berlin'.")],
) -> str:
    """Return the current weather for a city."""
    # In a real app this would hit a weather API. Hardcoded for the lesson.
    faked = {
        "berlin": "12°C, overcast",
        "vienna": "15°C, sunny",
        "munich": "10°C, light rain",
    }
    return faked.get(city.lower(), f"weather data unavailable for {city}")


def get_time(
    timezone: Annotated[str, Field(description="IANA timezone name, e.g. 'Europe/Berlin'.")],
) -> str:
    """Return the current local time for a timezone."""
    # Using a fixed answer so the lesson is deterministic.
    # Real implementation: zoneinfo.ZoneInfo(timezone) + datetime.now(tz=...)
    return f"It is currently {datetime.now().strftime('%H:%M')} in {timezone}."


async def main() -> None:
    agent = OpenAIChatCompletionClient().as_agent(
        name="TravelHelper",
        instructions=(
            "You help travelers. Use the provided tools to look up weather "
            "and local time when asked. Keep answers concise."
        ),
        tools=[get_weather, get_time],
    )

    prompt = "What's the weather in Berlin and what time is it there?"
    print(f"User: {prompt}\n")

    result = await agent.run(prompt)
    print(f"Agent: {result.text}")


if __name__ == "__main__":
    asyncio.run(main())
