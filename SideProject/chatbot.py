from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.agents import initialize_agent
from langchain.agents import AgentType
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/calendar'])

service = build('calendar', 'v3', credentials=creds)



@tool
def add_calendar_event(user_input: str) -> str:
    """
    사용자의 요청을 분석하여 Google Calendar에 일정을 추가하는 함수.
    예: "내일 오후 3시에 카페에서 팀 미팅 등록해줘"
    """

    print("user input : " + user_input)
    a = ("현재 시간은 2025-02-26 13:16이야 뒤 ()에 나오는 시간을 YYYY-MM-DDTHH:MM:SS 형식으로 변환해주고 예약 내용은 '|' 뒤에 구분해서 붙여줘 "
         "단, 날짜와 시간은 절대 틀리지 않도록 주의하고, 원본과 동일하게 변환해야 해"
         "예약해줘에서 '예약' 이라는 단어부터는 내용에 포함할 필요 없어"
         "예시1: 2025-02-26T14:00:00 | 자동차 정비"
         "예시2: 2025-02-26T14:00:00 | 헬스장 방문"
         "예시3: 2025-02-26T14:00:00 | 치과 방문"
         "(") + user_input + ")"
    #print(a)

    result = llm.invoke(a)
    #print(result)
    response = getattr(result, 'content', None).split("|")
    #print(response)
    parsed_date = response[0].strip()  # content 속성에 접근
    parsed_cont = response[1].strip()

    print("Parsing date : " + str(parsed_date))
    print("Parsing cont : " + str(parsed_cont))

    if not parsed_date:
        return "날짜를 이해하지 못했어요. 다시 입력해 주세요."

    # 기본 종료 시간: 시작 시간 + 1시간
    start_time = parsed_date
    end_time = parsed_date

    return 


# LLM 모델 초기화
llm = ChatOpenAI(model="gpt-4o-mini")

# 사용할 Tool 목록
tools = [add_calendar_event]

# Agent 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # AI가 Tool을 선택하게 함
    verbose=True
)


# 대화 이력 저장 리스트
conversation_history = [
    SystemMessage(content="너는 친절한 AI 챗봇이야. 사용자의 질문에 성실하게 답변해줘.")
]
# ---------------------------------------------------------------------------------#
with st.sidebar:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    st.title("💬 Chatbot")
    st.caption("🚀 A Streamlit chatbot powered by OpenAI")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input():


        st.chat_message("user").write(user_input)


        response = ""
        if "예약" in user_input or "일정 등록" in user_input:
            print("🔹 일정 예약 요청 감지 → Agent 실행")
            response = agent.invoke(user_input)
            response = response.get('output')
            conversation_history.append(AIMessage(content=response))


        else:
            print("🔹 일반 질문 처리 → LLM 실행")
            response = llm.invoke(conversation_history)
            print(response.content)
            response = response.content
            conversation_history.append(AIMessage(content=response))

        st.chat_message("assistant").write(response)