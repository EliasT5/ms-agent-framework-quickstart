"""
Unit 0 — Sanity check.

Goal: prove your environment is configured correctly.
Run: python agent.py
"""

import asyncio

from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    agent = OpenAIChatCompletionClient().as_agent(
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep answers to one sentence.",
    )

    result = await agent.run("Say hello in one short sentence.")
    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
