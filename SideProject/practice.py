import  datetime
from datetime import datetime, timedelta
import  time

from click import prompt
from django.contrib.messages.context_processors import messages
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

import speech_recognition as sr
from gtts import  gTTS
import os
import  playsound
from pyexpat.errors import messages
from translate import Translator

from dotenv import load_dotenv
import os

import openai
from config import *

openai.api_key = os.getenv("OPENAI_API_KEY")

def textToVoice(text):
    tts = gTTS(text=text, lang='ko')
    filename = 'voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

def voiceToText():
    r = sr.Recognizer()
    with sr.Microphone() as source:

        try:
            print("🎤 환경 소음 조정 중... (1초만 기다려 주세요)")
            r.adjust_for_ambient_noise(source, duration=1)

            print("Say something!!!")
            audio = r.listen(source, timeout=5)  # ⏳ 5초 동안 기다림

            said = r.recognize_google(audio, language='ko-KR')
            print("Your speech thinks like: ", said)

        except sr.WaitTimeoutError:
            print("⏳ 타임아웃: 아무 소리도 감지되지 않았습니다. 마이크를 확인하세요!")
        except sr.RequestError:
            print("❌ 오류: Google API 요청 실패. 인터넷 연결 확인하세요!")
        except sr.UnknownValueError:
            print("🔇 음성 인식 실패: 음성이 명확하지 않습니다.")
        except Exception as e:
            print(f"🚨 예외 발생: {e}")

    return said

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis/auth/calendar'])
service = build('calendar', 'v3', credentials=creds)

def create_event(start_time, end_time, summary, location = None, description = None):

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start' :
        {
            'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'Asia/Seoul'
        },
        'end' :
        {
            'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'Asia/Seoul'
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print("Event created! : " + event.get("htmlLink"))




def register_schedule():

    my_res = "yes"
    if my_res == "yes":
        print("일정등록을 위한 몇가지 질문을 드리겠습니다.")
        textToVoice("일정 등록을 위한 질문을 드리겠습니다.")
        print("등록일자를 알려주세요. 예를 들어 '2023년 4월 20일 오후 7시'인 경우 '2023 0420 19' 라고만 말씀해 주세요.")
        textToVoice("등록일자를 알려주세요. 예를 들어 '2023년 4월 20일 오후 7시'인 경우 '2023 0420 19' 라고만 말씀해 주세요.")

        my_res_date = voiceToText()

        print("등록할 일정의 내용을 말씀해 주세요")
        textToVoice("등록할 일정의 내용을 말씀해 주세요.")
        my_res_cont = voiceToText()

        print(my_res_cont, "과", my_res_cont, "으로 등록하겠습니다. 내용이 맞으면 yes, 틀리면 no라고 말씀해주세요")
        textToVoice(str(my_res_cont) + "과" + str(my_res_cont) + "으로 등록하겠습니다. 내용이 맞으면 yes, 틀리면 no라고 말씀해주세요")

        my_res_yesno = voiceToText()

        if(my_res_yesno == "yes"):
            try:
                my_res_date = my_res_date.replace(" ", "").strip()
                year = my_res_date[0:4]
                month = my_res_date[4:6]
                day = my_res_date[6:8]
                hour = my_res_date[8:10]

                time_obj = datetime.strptime(my_res_date, "%Y%m%d%H")
                time_obj += timedelta(hours = 1)
                time_str_formatted = time_obj.strftime("%Y%m%d%H%M%S")

                hour2 = str(time_str_formatted)[8:10]


                minute = "0"
                second = "0"


                start_time = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
                end_time = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))


                summary = my_res_cont
                location = ' '
                description = my_res_cont


                create_event(start_time, end_time, summary, location, description)
                print("구글캘린더에 홍길동과 점심약속으로 2023년 4월 20일 오후 7시로 등록되었습니다.")
                textToVoice("구글캘린더에 홍길동과 점심약속으로 2023년 4월 20일 오후 7시로 등록되었습니다.")
                print("지피티모드를 종료하고 대기모드로 돌아갑니다. 제가 필요하면 대기모드에서 '지피티'라고 불러주세요")
                textToVoice("지피티모드를 종료하고 대기모드로 돌아갑니다. 제가 필요하면 대기모드에서 '지피티'라고 불러주세요")
            except HttpError as error:
                print(error)
                textToVoice("에러가 발생했습니다.. 지피티 모드를 종료합니다.")
        else:
            print("내용이 잘못 입력되었습니다.다시 등록하려면 yes, 여기서 나가시려면 no라고 대답해주세요")
            textToVoice("내용이 잘못 입력되었습니다.다시 등록하려면 yes, 여기서 나가시려면 no라고 대답해주세요")
            my_res_yesno = voiceToText()
            if(my_res_yesno == "yes"):
                register_schedule()
                pass
            else:
                pass


#print(sr.Microphone.list_microphone_names())

content = ''
for_break = True
while True:
    if for_break == False:
        break
    print("챗지피티와 대화하려면 '지피티'라고 불러주시고, 대화를 종료하려면 '굿바이'라고 말씀해 주세요")
    textToVoice("챗지피티와 대화하려면 '지피티'라고 불러주시고, 대화를 종료하려면 '굿바이'라고 말씀해 주세요")
    my_res = voiceToText()

    if '굿바이' in my_res:
        textToVoice("chatGPT를 종료합니다.")
        print("chatGPT를 종료합니다.")
        break

    if 'GPT' in my_res:
        print("지피티 모드입니다.")
        textToVoice("지피티 모드입니다.")

        while True:

            now = datetime.now()
            delta = timedelta(seconds=5)
            after_30sec =  now + delta

            print("네 주인님 말씀하세요")
            textToVoice("네 주인님 말씀하세요")
            my_res1 = voiceToText()

            if '굿바이' in my_res1:
                textToVoice("chatGPT를 종료합니다.")
                print("chatGPT를 종료합니다.")
                for_break = False

            now = datetime.now()

            if my_res1 == " " and (now > after_30sec):
                print("5초 동안 아무 움직임이 없어 지피티모드를 종료합니다.('대기 모드로 돌아갑니다.')")
                textToVoice("5초 동안 아무 움직임이 없어 지피티모드를 종료합니다.('대기 모드로 돌아갑니다.')")
                time.sleep(1)
                break
            elif "일정" in my_res1:
                print("구글캘린더에 일정을 추가할 수 있습니다. 일정을 등록하기 위해서는 구글 캘린더 플러그인을 설치해야 합니다. \ 설치할까요? yes or no로 답변해주세요")
                textToVoice("구글캘린더에 일정을 추가할 수 있습니다. 일정을 등록하기 위해서는 구글 캘린더 플러그인을 설치해야 합니다. \ 설치할까요? yes or no로 답변해주세요")

                my_res2 = voiceToText()

                if my_res2 == "yes" or my_res2 == "예스":
                    print("구글캘린더 플러그인을 설치하였습니다.")
                    textToVoice("구글캘린더 플러그인을 설치하였습니다.")
                    print("일정들록을 위한 몇가지 질문을 드리겠습니다.")
                    textToVoice("일정들록을 위한 몇가지 질문을 드리겠습니다.")

                    print("등록일자를 알려주세요. 예를 들어 '2023년 4월 20일 오후 7시'인 경우 '2023 0420 19' 라고만 말씀해 주세요.")
                    textToVoice("등록일자를 알려주세요. 예를 들어 '2023년 4월 20일 오후 7시'인 경우 '2023 0420 19' 라고만 말씀해 주세요.")

                    my_res_date = voiceToText()

                    print("등록할 일정의 내용을 말씀해주세요")
                    my_res_cont = voiceToText()

                    print(my_res_cont, "과", my_res_cont, "으로 등록하겠습니다. 내용이 맞으면 yes, 틀리면 no라고 말씀해주세요")
                    textToVoice(str(my_res_cont) + "과" + str(my_res_cont) + "으로 등록하겠습니다. 내용이 맞으면 yes, 틀리면 no라고 말씀해주세요")

                    my_res_yesno = voiceToText()

                    if(my_res_yesno == "yes"):
                        try:
                            my_res_date = my_res_date.replace(" ", "").strip()
                            year = my_res_date[0:4]
                            month = my_res_date[4:6]
                            day = my_res_date[6:8]
                            hour = my_res_date[8:10]

                            time_obj = datetime.strptime(my_res_date, "%Y%m%d%H")
                            time_obj += timedelta(hours = 1)
                            time_str_formatted = time_obj.strftime("%Y%m%d%H%M%S")

                            hour2 = str(time_str_formatted)[8:10]


                            minute = "0"
                            second = "0"


                            start_time = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
                            end_time = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))


                            summary = my_res_cont
                            location = ' '
                            description = my_res_cont


                            create_event(start_time, end_time, summary, location, description)
                            print("구글캘린더에 홍길동과 점심약속으로 2023년 4월 20일 오후 7시로 등록되었습니다.")
                            textToVoice("구글캘린더에 홍길동과 점심약속으로 2023년 4월 20일 오후 7시로 등록되었습니다.")
                            print("지피티모드를 종료하고 대기모드로 돌아갑니다. 제가 필요하면 대기모드에서 '지피티'라고 불러주세요")
                            textToVoice("지피티모드를 종료하고 대기모드로 돌아갑니다. 제가 필요하면 대기모드에서 '지피티'라고 불러주세요")
                        except HttpError as error:
                            print(error)
                            textToVoice("에러가 발생했습니다.. 지피티 모드를 종료합니다.")
                    else:
                        print("내용이 잘못 입력되었습니다.다시 등록하려면 yes, 여기서 나가시려면 no라고 대답해주세요")
                        textToVoice("내용이 잘못 입력되었습니다.다시 등록하려면 yes, 여기서 나가시려면 no라고 대답해주세요")
                        my_res_yesno = voiceToText()
                        if(my_res_yesno == "yes"):
                            register_schedule()
                            pass
                        else:
                            pass

                else:
                    print("구글달력 플러그인을 설치하지 않았습니다.")
                    voiceToText("구글달력 플러그인을 설치하지 않았습니다.")
                    print("지피티모드를 종료하고 대기모드로 돌아갑니다.")
                    voiceToText("지피티모드를 종료하고 대기모드로 돌아갑니다.")
            else:
                prompt = my_res1
                try:
                    messages = [
                        {'role' :'system', 'content' : 'You are a helpful assistant.'},
                        {'role' : 'user', 'content' : content},
                    ]
                    messages.append({'role' : 'assistant', 'content' : msg})
                    messages.append({'role': 'assistant', 'content': prompt})
                except:
                    messages = [
                        {'role' :'system', 'content' : 'You are a helpful assistant.'},
                        {'role' : 'user', 'content' : content},
                    ]
                response = openai.ChatCompletion.create(
                    model = 'gpt-3.5-turbo',
                    messages = messages
                )

                print("---------------------------------------------------------")
                print(str(response['choices'][0]['message']['content']).strip())
                msg = str(response['choices'][0]['message']['content']).strip()
                print("---------------------------------------------------------")

                textToVoice(msg)

                content = content + msg
    else:
        print("대기모드 입니다.")
        textToVoice("대기모드 입니다.")

    time.sleep(1)