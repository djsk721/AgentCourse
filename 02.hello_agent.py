from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
import asyncio
import os
from agent_framework import tool

load_dotenv()


async def main():
    print("Hello Agent")

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    model = os.getenv("AZURE_OPENAI_CHAT_MODEL")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    azure_client = AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )
    
    agent = OpenAIChatClient(
        async_client=azure_client,
        model=model,
        instruction_role="you are helpful friend."                       # instruction_role (지시 역할)
    ).as_agent(
        name="HelloAgent",
        instructions="한국말로 답변하세요."
    )
    result = await agent.run("What's the weather in Seoul?")                # instruction (지시사항)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
