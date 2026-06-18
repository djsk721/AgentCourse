from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
import asyncio
import os
from agent_framework import tool, Agent
from pydantic import Field
from typing import Annotated
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

load_dotenv()

search = DuckDuckGoSearchResults(
    api_wrapper=DuckDuckGoSearchAPIWrapper(
        region="kr-kr",
        safesearch="moderate",
        time="d",
        max_results=5
    ),
    output_format="list"
)

@tool
def web_search(
    query: Annotated[str, Field(
        description="사용자가 찾고자 하는 구체적인 검색어"
    )]
) -> str:
    """
    Search the web for current information.
    """
    results = search.invoke(query)

    print("raw search results:", results)
    print("type:", type(results))

    if not results:
        return "검색 결과를 찾지 못했습니다."

    # 1) 결과가 문자열이면 그대로 반환
    if isinstance(results, str):
        return results

    # 2) 결과가 dict 하나면 list로 감싸기
    if isinstance(results, dict):
        results = [results]

    # 3) 결과가 list인 경우 처리
    if isinstance(results, list):
        formatted_results = []

        for idx, item in enumerate(results[:5], start=1):
            # item이 dict인 경우
            if isinstance(item, dict):
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")

                formatted_results.append(
                    f"[{idx}] {title}\n"
                    f"내용: {snippet}\n"
                    f"출처: {link}"
                )

            # item이 문자열인 경우
            elif isinstance(item, str):
                formatted_results.append(
                    f"[{idx}] {item}"
                )

        return "\n\n".join(formatted_results)
    
    print("\n\n".join(formatted_results))

    return str(results)

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

    client = OpenAIChatClient(
        async_client=azure_client,
        model=model,
        instruction_role="you are helpful assistant."                       # instruction_role (지시 역할)
    )

    # web_search_tool = client.get_web_search_tool(
    #     user_location={"city": "Seattle", "region": "US"},
    # )

    agent = Agent(
        name="HelloAgent",
        client=client,
        instructions="reponse with korean with use tool.",
        tools=[web_search],
    )
    session = agent.create_session()

    while True:
        user_prompt = input("\n사용자 입력: ")
        if user_prompt == 'exit':
            break
        # result = await agent.run(user_prompt, session=session)
        print('\n')
        async for chunk in await agent.run(user_prompt, stream=True, session=session):
            if chunk.text:
                print(chunk.text, end="", flush=True)
    
if __name__ == "__main__":
    asyncio.run(main())
