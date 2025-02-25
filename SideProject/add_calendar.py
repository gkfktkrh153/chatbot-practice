import datetime
from google.oauth2.credentials import Credentials
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

# API 인증 정보
creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/calendar'])

# 구글 캘린더 API 클라이언트 생성
service = build('calendar', 'v3', credentials=creds)

# 일정 등록 함수
def create_event(start_time, end_time, summary, location=None, description=None):
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'Asia/Seoul',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')

# 일정 등록 예시
start_time = datetime.datetime(2023, 4, 22, 20, 0, 0)
end_time = datetime.datetime(2023, 4, 22, 21, 0, 0)
summary = 'Test Event3'
location = 'Seoul, South Korea'
description = 'This is a test event'

try:
    create_event(start_time, end_time, summary, location, description)
except HttpError as error:
    print(f'An error occurred: {error}')
