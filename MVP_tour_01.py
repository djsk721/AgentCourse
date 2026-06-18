from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from agent_framework import tool, Agent

import asyncio
import os
from typing import Annotated
from pydantic import Field
from random import randint

load_dotenv()

# Tools
def get_weather(location: Annotated[str, Field(description="날씨를 확인하려는 도시 또는 지역명")]) -> str:
    """주어진 위치에 대한 날씨 정보를 반환하는 도구 함수입니다. """
    conditions = ["맑음", "흐림", "비", "눈"]
    print(f"Tool called: get_weather for location: {location}")
    return f"{location}의 날씨는 {conditions[randint(0,3)]}입니다. 기온은 {randint(10,30)}도입니다."

def get_exchange_rate(
        base_currency: Annotated[str, Field(description="기준 통화 코드 (ex: USD, KRW, EUR)")],
        target_currency: Annotated[str, Field(description="목적 통화 코드 (ex: USD, KRW, EUR)")]) -> str:
    """두 통화간의 실시간 환율 정보를 가져올 수 있다. """
    print(f"Tool called: 시스템 환율 정보를 가져와서 대답하는 함수")
    
    print(f"환율 도구 호출 중: {base_currency} -> {target_currency}")

    if target_currency == "KRW":
        rate = randint(1300, 1500) / 100
    else:
        rate = randint(80, 150) / 100
    
    return f"현재 {base_currency}에서 {target_currency}로의 환율은 약 {rate}입니다."


async def main():
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
        instruction_role="당신은 여행사 'MVP Tour'의 20년 경력의 상담원입니다."                       # instruction_role (지시 역할)
    ).as_agent(
        name="MVP-Tour",
        instructions="""
고객에게 정중하게 인사하고, 여행 계획에 대해 도움을 줄 준비가 되었음을 알리세요.
답변 끝에는 항상 '즐거운 여행의 시작, MVP Tour입니다!'라는 문구를 붙여주세요.
""",
        tools=[get_weather, get_exchange_rate],
    )
    
    agent = OpenAIChatClient(
        async_client=azure_client,
        model=model,
        instruction_role="당신은 여행사 'MVP Tour'의 20년 경력의 상담원입니다."                       # instruction_role (지시 역할)
    ).as_agent(
        name="MVP-Tour",
        instructions="""
고객에게 정중하게 인사하고, 여행 계획에 대해 도움을 줄 준비가 되었음을 알리세요.
답변 끝에는 항상 '즐거운 여행의 시작, MVP Tour입니다!'라는 문구를 붙여주세요.
""",
        tools=[get_weather, get_exchange_rate],
    )
    print(f"에이전트 {agent.name}가 시작되었습니다.")

    while True:
        user_input = input("사용자: ")
        if user_input.lower() in ["exit", "quit"]:
            print("에이전트를 종료합니다. 즐거운 여행의 시작, MVPTour입니다!")
            break

        response = await agent.run(user_input)
        print(f"에이전트: {response}")

if __name__ == "__main__":
    asyncio.run(main())