import datetime
from google.oauth2.credentials import Credentials  # pip install --upgrade google-api-python-client
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from datetime import datetime, time, timedelta

# API 인증 정보
# creds = Credentials.from_authorized_user_file('credentials.json',
# ['https://www.googleapis.com/auth/calendar']) # 이거가 다름에 아래로 바꿔야 함
creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/calendar'])

# 구글 캘린더 API 클라이언트 생성
service = build('calendar', 'v3', credentials=creds)

start_date = datetime(2023, 4, 20).isoformat() + 'Z'  # Z 는 UTC 시간을 의미합니다.
end_date = datetime(2023, 4, 23).isoformat() + 'Z'

events_result = service.events().list(calendarId='primary', timeMin=start_date,
    timeMax=end_date, singleEvents=True, orderBy='startTime').execute()
events = events_result.get('items', [])

for event in events:
    # 일치하는 일정을 찾으면 삭제합니다.
    # print(event['summary'])
    if event['summary'] == 'Test Event3':
        service.events().delete(calendarId='primary',
            eventId=event['id']).execute()
        print('일정이 삭제되었습니다.')
