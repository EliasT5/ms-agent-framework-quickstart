"""
Unit 1 — First agent: streaming vs. non-streaming.

Goal: feel the difference between getting the whole response at once
vs. watching it type itself out.

Run: python agent.py
"""

import asyncio

from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    agent = OpenAIChatCompletionClient().as_agent(
        name="PirateAgent",
        instructions=(
            "You are a terse pirate. "
            "Reply in two short sentences, using pirate vocabulary."
        ),
    )

    question = "What is the best way to learn programming?"

    # --- Non-streaming: wait for the full response, print once ---
    print("=== Non-streaming (agent.run) ===")
    result = await agent.run(question)
    print(result.text)
    print()

    # --- Streaming: print each chunk as it arrives ---
    print("=== Streaming (agent.run(..., stream=True)) ===")
    async for chunk in agent.run(question, stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()  # trailing newline


if __name__ == "__main__":
    asyncio.run(main())
