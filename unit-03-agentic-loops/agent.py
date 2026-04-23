"""
Unit 3 — Agentic loops, with middleware to watch the loop.

Goal: give the agent a multi-step task, attach middleware that logs every
tool call, and watch the plan→act→observe→repeat cycle unfold.

Run: python agent.py
"""

import asyncio
import sys
from collections.abc import Awaitable, Callable
from typing import Annotated

# On Windows, stdout defaults to cp1252 which can't encode → ← in the tool
# logs — a crash in middleware shows up as "tool failed" to the agent.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from agent_framework import FunctionInvocationContext, function_middleware
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()


def _args_to_dict(args) -> dict:
    """Coerce FunctionInvocationContext.arguments (BaseModel or Mapping) into a plain dict."""
    if args is None:
        return {}
    if hasattr(args, "model_dump"):
        return args.model_dump()
    try:
        return dict(args)
    except (TypeError, ValueError):
        return {"_repr": str(args)}


# --- Tools ----------------------------------------------------------------
# All return hardcoded data. In a real agent these would hit real APIs.


def get_weather(
    city: Annotated[str, Field(description="City name.")],
    date: Annotated[str, Field(description="Date like 'today' or 'tomorrow'.")],
) -> str:
    """Get overall weather (temperature and conditions) for a city on a date."""
    return f"{city} on {date}: 18°C, partly sunny"


def get_forecast_hourly(
    city: Annotated[str, Field(description="City name.")],
) -> str:
    """Get the hourly forecast for today and tomorrow."""
    return f"{city}: morning light rain, clear from noon onward, dry evening"


def find_parks(
    city: Annotated[str, Field(description="City name.")],
) -> str:
    """List parks in a city suitable for a group picnic."""
    return f"{city} parks: Stadtpark (central), Prater (large, popular), Augarten (quieter)"


def suggest_food(
    weather: Annotated[str, Field(description="Short weather description, e.g. 'sunny 18°C'.")],
) -> str:
    """Suggest picnic food suitable for given weather conditions."""
    if "rain" in weather.lower() or "cold" in weather.lower():
        return "warm soups in thermos, hearty sandwiches, hot tea"
    return "light salads, fresh fruit, cold drinks, crusty bread"


# --- Middleware: make the loop visible -----------------------------------


@function_middleware
async def log_tool_calls(
    context: FunctionInvocationContext,
    call_next: Callable[[], Awaitable[None]],
) -> None:
    """Print every tool call before and after it runs."""
    name = context.function.name
    args = _args_to_dict(context.arguments)
    print(f"  [→] {name}({args})")

    await call_next()

    result = context.result
    # Truncate long results so the log stays readable.
    result_str = str(result)
    if len(result_str) > 100:
        result_str = result_str[:100] + "..."
    print(f"  [←] {name} → {result_str}")


# --- Run -----------------------------------------------------------------


async def main() -> None:
    agent = OpenAIChatCompletionClient().as_agent(
        name="PicnicPlanner",
        instructions=(
            "You help plan picnics. Use the tools to gather weather, forecast, "
            "nearby parks, and food suggestions before giving a final plan. "
            "Keep the final plan to 3-4 sentences."
        ),
        tools=[get_weather, get_forecast_hourly, find_parks, suggest_food],
        middleware=[log_tool_calls],
    )

    prompt = (
        "Plan a picnic for tomorrow in Vienna. Tell me the best time of day, "
        "where to go, and what to bring."
    )
    print(f"User: {prompt}\n")
    print("Tool calls:")

    result = await agent.run(prompt)

    print(f"\nAgent:\n{result.text}")


if __name__ == "__main__":
    asyncio.run(main())
