import openai 
import os
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv('.env')

client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
    api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
)

# ===== Streamlit UI =====
st.set_page_config(page_title="Azure OpenAI Chatbot", page_icon="💬")
st.title("💬 Azure OpenAI Chatbot")

if not os.getenv('AZURE_OPENAI_API_KEY'):
    st.error("AZURE_OPENAI_API_KEY가 설정되지 않았습니다.")
    st.stop()

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a awesome assistant."
        }
    ]

# 기존 대화 출력
for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
user_input = st.chat_input("메시지를 입력하세요")

if user_input:
    # 사용자 메시지 저장 및 출력
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # 모델 응답
    with st.chat_message("assistant"):
        with st.spinner("응답 생성 중..."):
            response = client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_CHAT_MODEL'),
                messages=st.session_state.messages,
            )

            assistant_message = response.choices[0].message.content
            st.markdown(assistant_message)

    # assistant 응답 저장
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message
        }
    )

# 대화 초기화 버튼
if st.sidebar.button("대화 초기화"):
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a awesome assistant."
        }
    ]
    st.rerun()