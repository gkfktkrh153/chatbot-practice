import  datetime
from datetime import datetime, timedelta
import  time


from anyio import sleep
from click import prompt
from django.contrib.messages.context_processors import messages
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

import speech_recognition as sr
from gtts import  gTTS
import  playsound
from pyexpat.errors import messages
from translate import Translator

from dotenv import load_dotenv
import os

import openai
from config import *
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.agents import initialize_agent
from langchain.agents import AgentType
import dateparser

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def textToVoice(text):
    print(text)
    tts = gTTS(text=text, lang='ko')
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename, True)  # 동기적 실행 (재생이 끝날 때까지 대기)
    os.remove(filename)  # 파일 삭제


def voiceToText():
    said = input("입력 : ")
    return said


creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/calendar'])

service = build('calendar', 'v3', credentials=creds)

@tool
def add_calendar_event(user_input: str) -> str:


    print("user input : " + user_input)
    a = ("현재 시간은 2025-02-26 13:16이야 뒤 ()에 나오는 시간을 YYYY-MM-DDTHH:MM:SS 형식으로 변환해주고 예약 내용은 '|' 뒤에 구분해서 붙여줘 "
         "단, 날짜와 시간은 절대 틀리지 않도록 주의하고, 원본과 동일하게 변환해야 해"
         "예시1: 2025-02-26T14:00:00 | 자동차 정비"
         "예시2: 2025-02-26T14:00:00 | 헬스장 방문"
         "예시3: 2025-02-26T14:00:00 | 치과 예약"
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

    event = {
        "summary": parsed_cont,
        'location': "",
        'description': "",
        "start": {"dateTime": start_time, "timeZone": "Asia/Seoul"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Seoul"},
    }

    event = service.events().insert(calendarId="primary", body=event).execute()
    return f"📅 일정이 등록되었습니다! 확인 링크: {event.get('htmlLink')}"


# LLM 모델 초기화
llm = ChatOpenAI(model="gpt-4")

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

print("안녕하세요! 무엇이든 질문하세요. 'exit'을 입력하면 종료됩니다.")

while True:
    user_input = input("사용자: ")
    if user_input.lower() == "exit":
        print("대화를 종료합니다.")
        break

    # 사용자 입력을 대화 이력에 추가
    conversation_history.append(HumanMessage(content=user_input))


    response = ""
    if "예약" in user_input or "일정 등록" in user_input:
        print("🔹 일정 예약 요청 감지 → Agent 실행")
        response = agent.invoke(user_input)
        conversation_history.append(AIMessage(content=response.get('output')))


    else:
        print("🔹 일반 질문 처리 → LLM 실행")
        response = llm.invoke(conversation_history)
        print(response)
        conversation_history.append(AIMessage(content=response.content))

    print(conversation_history)
    # AI 응답을 대화 이력에 추가


