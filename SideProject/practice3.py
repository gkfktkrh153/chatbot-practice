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
import json
from django.core.serializers.json import DjangoJSONEncoder
import openai
from config import *
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.agents import initialize_agent
from langchain.agents import AgentType
import dateparser

import os
import sys
import django

# Django 설정 파일 지정 (프로젝트명.settings 수정)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 한 단계 위로 이동
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SideProject.settings")
django.setup()

# 이제 Django 모델 import 가능
from SideProject.models import Employees

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# LLM 모델 초기화
llm = ChatOpenAI(model="gpt-4o-mini")

class Person:
    def __init__(self, name="Unknown", age=0):
        self.name = name
        self.age = age

    def getData(self):
        # GPT가 이해하기 쉬운 방식으로 출력
        return f"name : {self.name}, age : {self.age}"

# 대화 이력 저장 리스트
conversation_history = [
    SystemMessage(content="너는 친절한 AI 챗봇이야. 사용자의 질문에 성실하게 답변해줘.")
]

print("안녕하세요! 무엇이든 질문하세요. 'exit'을 입력하면 종료됩니다.")


def recommendByCustomerData():
    person = Person("지승용")

    question = (
        "이 데이터를 가지고 사원을 조회하는 쿼리 좀 작성해줘. "
        "단, 유의미한 값만 조건으로 사용하고('age'가 0이거나 'name'이 'unknown'이면 조건절에 추가하지 않아도 돼.)"
        "응답은 오직 SQL 쿼리문만 주면 돼"
        "결과는 절대로 sql''' '''와 같은 형식으로 묶지 말고, 순수한 텍스트로만 제공해줘."
        "예시: select * from employees where name = 'John Doe' and age = 30"
        + person.getData())

    query = llm.invoke(question).content
    print("Query : " + query)
    result =  Employees.objects.raw(query)
    data = [{"id": emp.id, "name": emp.name, "age": emp.age} for emp in result]

    # JSON 변환
    json_data = json.dumps(data, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)
    return json_data


def selectResearchingOption():
    question = (
        "최근 사용된 SQL 쿼리에서 사용된 파라미터 값을 뽑아줘"
        "형식은 예시와 같았으면 좋겠어"
        "결과는 절대로 ''' '''와 같은 형식으로 묶지 말고, 순수한 텍스트로만 제공해줘."
        "예시 :\n name=value \n age=value"
    )
    conversation_history.append(HumanMessage(content=question))
    result = llm.invoke(conversation_history)

    return result.content


def extractIntention(user_input):
    question = (
            "다음 질문의 의도를 분석해줘. "
            "질문의 목적이 검색이라면 'research', 검색 조건을 알고 싶다면 'option'을 반환해. "
            "그 외의 경우에는 'unknown'을 반환해. "
            "반환할 때는 반드시 단일 문자열 값만 응답해. "
            "예시:\n"
            "- '사용자 정보 기반으로 검색해줘' -> 'research'\n"
            "- '방금 사용한 검색 조건이 뭔지 알려줘' -> 'option'\n"
            "- '안녕?' -> 'unknown'\n"
            "\n"
            "질문: " + user_input
    )

    result = llm.invoke(question)

    return result.content

while True:
    user_input = input("사용자: ")
    if user_input.lower() == "exit":
        print("대화를 종료합니다.")
        break

    # 사용자 입력을 대화 이력에 추가
    conversation_history.append(HumanMessage(content=user_input))

    response = ""

    # 질문 의도 파악
    questionIntention = extractIntention(user_input)

    print(questionIntention)
    # 맥락상 고객 기반 데이터로 조회해줘라면
    if questionIntention == "research":
        response = recommendByCustomerData()
    # 맥락상 검색 조건 전체를 필요로 한다면
    elif questionIntention == "option":
        response = selectResearchingOption()


    print(response)
    conversation_history.append(AIMessage(content=response))


#    print("*********************** 대화내역 *********************** ")
#    for chat in conversation_history:
#        print(chat.content)