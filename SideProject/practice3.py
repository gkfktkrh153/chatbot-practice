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
        "예시: select * from employee where name = 'John Doe' and age = 30"
        + person.getData())
    result = llm.invoke(question)

    return result.content


def selectResearchingOption():
    question = (
        "방금 작성된 SQL 쿼리에서 사용된 파라미터 값을 뽑아줘"
        "형식은 예시와 같았으면 좋겠어"
        "결과는 절대로 ''' '''와 같은 형식으로 묶지 말고, 순수한 텍스트로만 제공해줘."
        "예시 :\n name=value \n age=value"
    )
    conversation_history.append(HumanMessage(content=question))
    result = llm.invoke(conversation_history)

    return result.content



while True:
    user_input = input("사용자: ")
    if user_input.lower() == "exit":
        print("대화를 종료합니다.")
        break

    # 사용자 입력을 대화 이력에 추가
    conversation_history.append(HumanMessage(content=user_input))

    response = ""
    # 맥락상 고객 기반 데이터로 조회해줘라면
    if user_input == "customer":
        response = recommendByCustomerData()
    # 맥락상 검색 조건 전체를 필요로 한다면
    elif user_input == "option":
        response = selectResearchingOption()


    print(response)
    conversation_history.append(AIMessage(content=response))


    print("*********************** 대화내역 *********************** ")
    for chat in conversation_history:
        print(chat.content)