from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from agent_framework import tool, Agent
from pydantic import Field
import chromadb
from langchain_tavily import TavilySearch

import asyncio
import os
from typing import Annotated, Any
from random import randint
import requests
from requests.exceptions import Timeout, RequestException


CITY_COORDS = {
    "서울": ("서울", "대한민국", 37.5665, 126.9780),
    "부산": ("부산", "대한민국", 35.1796, 129.0756),
    "제주": ("제주", "대한민국", 33.4996, 126.5312),
    "도쿄": ("도쿄", "일본", 35.6762, 139.6503),
    "오사카": ("오사카", "일본", 34.6937, 135.5023),
    "시애틀": ("시애틀", "미국", 47.6062, -122.3321),

    # 추가
    "수원": ("수원", "대한민국", 37.2636, 127.0286),
    "성남": ("성남", "대한민국", 37.4200, 127.1265),
}
# 1. ChromaDB 클라이언트 설정 (메모리 모드)
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="mvp_tour_info", metadata={"hnsw:space": "cosine"})

collection.add(
    documents=[
        "시애틀 투어 패키지: 3박 4일 일정으로 스페이스 니들 입장권이 포함되어 있으며, 시애틀 시내 반나절 투어가 제공됩니다.",
        "MVPTour 특별 환전 서비스: 본사 1층에서 오전 9시부터 오후 4시까지 USD, JPY, EUR에 대해 우대 환율을 제공합니다.",
        "예약 취소 규정: 여행 7일 전까지는 100% 환불 가능하며, 이후에는 50% 수수료가 발생합니다.",
        "오사카 자유여행 패키지: 2박 3일 일정으로 난바, 도톤보리, 유니버설 스튜디오 선택 관광이 포함되어 있습니다.",
        "항공권 변경 규정: 출발 3일 전까지는 1회 무료 변경이 가능하며, 이후 변경 시 항공사 수수료가 부과될 수 있습니다.",
        "단체 여행 할인 정책: 10명 이상 예약 시 총 상품가의 5% 할인이 적용되며, 20명 이상은 별도 견적이 제공됩니다.",
        "여행자 보험 안내: 모든 해외 패키지 상품에는 기본 여행자 보험이 포함되며, 고급형 보험은 추가 비용으로 선택할 수 있습니다.",
        "공항 픽업 서비스: 인천공항 및 김포공항 출발 고객에게 사전 예약 시 유료 픽업 서비스를 제공합니다.",
        "호텔 업그레이드 규정: 프리미엄 패키지 고객은 잔여 객실 상황에 따라 무료 객실 업그레이드가 제공될 수 있습니다.",
        "비자 발급 대행 서비스: 미국, 중국, 베트남 등 일부 국가에 대해 비자 발급 서류 검토 및 대행 서비스를 제공합니다."
    ],
    ids=[
        "doc1",
        "doc2",
        "doc3",
        "doc4",
        "doc5",
        "doc6",
        "doc7",
        "doc8",
        "doc9",
        "doc10"
    ]
)
print("📦 사내 지식 베이스 구축 완료!")

load_dotenv()

search = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="basic",
    include_answer=True,
    include_raw_content=False,
    include_images=False,
)

# [도구3] RAG
@tool(approval_mode="never_require")
def search_travel_docs(
    query: Annotated[str, Field(description="여행 상품이나 회사 규정에 대해 검색할 키워드")]
) -> str:
    """사내 지식베이스(ChromaDB)에서 여행 상품이나 회사 규정을 검색합니다."""
    print(f"🔍 [RAG] 지식베이스 검색 중: '{query}'")

    results = collection.query(
        query_texts=[query],
        n_results=3,
        include=["documents", "distances", "metadatas"]
    )

    print("RAG 질문:", query)
    print("검색 결과:", results)

    docs = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    if not docs:
        return "관련된 정보를 찾을 수 없습니다."

    formatted = []

    for rank, (doc_id, doc, distance) in enumerate(zip(ids, docs, distances), start=1):
        formatted.append(
            f"[{rank}] id={doc_id}, distance={distance:.4f}\n{doc}"
        )

    return "사내 지식베이스 검색 결과:\n\n" + "\n\n".join(formatted)
    
@tool(approval_mode="never_require")
def web_search_tool(
    query: Annotated[str, Field(description="사용자가 찾고자 하는 구체적인 검색어")]
) -> str:
    """Tavily를 사용해 웹 검색을 수행합니다."""
    print(f"\n[도구] Tavily 검색 도구 호출 중: {query}")

    try:
        results: Any = search.invoke({"query": query})
    except Exception as e:
        return f"검색 중 오류가 발생했습니다: {e}"

    print("Tavily raw results:", results)
    print("type:", type(results))

    if not results:
        return "검색 결과를 찾지 못했습니다."

    # langchain-tavily의 TavilySearch는 보통 dict 형태를 반환
    if isinstance(results, dict):
        answer = results.get("answer", "")
        result_items = results.get("results", [])

        formatted_results = []

        if answer:
            formatted_results.append(f"요약 답변: {answer}")

        for idx, item in enumerate(result_items[:5], start=1):
            title = item.get("title", "제목 없음")
            content = item.get("content", "")
            url = item.get("url", "")
            score = item.get("score", "")

            formatted_results.append(
                f"[{idx}] {title}\n"
                f"내용: {content}\n"
                f"출처: {url}\n"
                f"점수: {score}"
            )

        return "\n\n".join(formatted_results) if formatted_results else str(results)

    # 버전에 따라 list로 오는 경우도 방어
    if isinstance(results, list):
        formatted_results = []

        for idx, item in enumerate(results[:5], start=1):
            if isinstance(item, dict):
                title = item.get("title", "제목 없음")
                content = item.get("content", "")
                url = item.get("url", "")
                score = item.get("score", "")

                formatted_results.append(
                    f"[{idx}] {title}\n"
                    f"내용: {content}\n"
                    f"출처: {url}\n"
                    f"점수: {score}"
                )
            else:
                formatted_results.append(f"[{idx}] {item}")

        return "\n\n".join(formatted_results)

    return str(results)

@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, Field(description="날씨를 확인하려는 도시 또는 지역명")]
) -> str:
    """지정된 지역의 현재 날씨 정보를 가져옵니다."""
    print(f"🔍 [시스템] 날씨 도구 호출 중: {location}")

    try:
        location = location.strip()

        if location not in CITY_COORDS:
            return (
                f"❌ '{location}'은 현재 등록된 도시가 아닙니다.\n"
                f"지원 도시: {', '.join(CITY_COORDS.keys())}"
            )

        city, country, latitude, longitude = CITY_COORDS[location]

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,weather_code,wind_speed_10m",
                "temperature_unit": "celsius",
                "timezone": "Asia/Seoul",
            },
            timeout=(5, 20),
        )
        weather_response.raise_for_status()

        weather_data = weather_response.json()
        current = weather_data["current"]

        temperature = current["temperature_2m"]
        weather_code = current["weather_code"]
        wind_speed = current["wind_speed_10m"]

        weather_descriptions = {
            0: "맑음", 1: "대체로 맑음", 2: "부분 구름", 3: "흐림",
            45: "안개", 48: "안개",
            51: "이슬비", 53: "이슬비", 55: "이슬비",
            61: "약한 비", 63: "비", 65: "강한 비",
            71: "가벼운 눈", 73: "눈", 75: "무거운 눈",
            77: "눈 입자",
            80: "약한 소나기", 81: "소나기", 82: "강한 소나기",
            85: "가벼운 눈 소나기", 86: "강한 눈 소나기",
            95: "폭풍우", 96: "폭풍우와 우박", 99: "폭풍우와 큰 우박",
        }

        weather_desc = weather_descriptions.get(weather_code, f"알 수 없음({weather_code})")

        return (
            f"📍 {city}, {country}\n"
            f"🌡️ 현재 기온: {temperature}°C\n"
            f"☁️ 날씨: {weather_desc}\n"
            f"💨 풍속: {wind_speed} km/h"
        )

    except Timeout:
        return "❌ 날씨 API 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
    except RequestException as e:
        return f"❌ 날씨 API 요청 중 오류가 발생했습니다: {e}"
    except Exception as e:
        return f"❌ 날씨 정보를 처리하는 중 오류가 발생했습니다: {e}"

# [도구 2] 환율 조회 함수
@tool(approval_mode="never_require")
def get_exchange_rate(
    base_currency: Annotated[str, Field(description="기준 통화 코드 (예: USD, EUR)")],
    target_currency: Annotated[str, Field(description="대상 통화 코드 (예: KRW, JPY)")]
) -> str:
    """두 통화 간의 실시간 환율 정보를 가져옵니다."""
    print(f"🔍 [시스템] 환율 도구 호출 중: {base_currency} -> {target_currency}")
    
    try:
        # 실시간 환율 API 호출
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if target_currency in data['rates']:
            rate = data['rates'][target_currency]
            return f"현재 {base_currency} 대비 {target_currency}의 환율은 {rate:.2f}입니다."
        else:
            return f"❌ {target_currency} 통화 코드를 찾을 수 없습니다. 올바른 통화 코드를 입력해주세요."
    except requests.exceptions.Timeout:
        return "❌ 환율 서버 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."
    except requests.exceptions.RequestException as e:
        return f"❌ 환율 정보를 가져올 수 없습니다. 오류: {str(e)}"
    except Exception as e:
        return f"❌ 환율 조회 중 오류가 발생했습니다: {str(e)}"

async def main() -> None:
    print("MVP-Tour Agent")

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
        instruction_role="system"                       # instruction_role (지시 역할)
    )
    
    # web_search_tool = client.get_web_search_tool(
    #     user_location={"city": "Seattle", "region": "US"},
    # )

    agent = client.as_agent(
        name="MVP-Tour",
        instructions="""
당신은 여행사 'MVP Tour'의 20년 경력의 상담원입니다.
고객의 요청 사항에 '검색'이 들어간 경우 'web_search_tool' 도구를 호출하세요.
고객에게 정중하게 인사하고, 여행 계획에 대해 도움을 줄 준비가 되었음을 알리세요
답변 끝에는 항상 '즐거운 여행의 시작, MVP Tour입니다!'라는 문구를 붙여주세요.
""",
        tools=[web_search_tool, get_weather, get_exchange_rate, search_travel_docs],
    )
    
    print(f'에이전트 {agent.name}가 준비 되었습니다.')
    session = agent.create_session()

    while True:
        user_prompt = input("\n사용자 입력: ")
        print(f"[나] : {user_prompt}")
        if user_prompt == 'exit':
            break
        # result = await agent.run(user_prompt, session=session)
        print('\n')
        async for chunk in await agent.run(user_prompt, stream=True, session=session):
            if chunk.text:
                print(chunk.text, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
