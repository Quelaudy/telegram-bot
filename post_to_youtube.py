import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    'https://www.googleapis.com/auth/drive.file'
]

def authenticate_youtube():
    """Авторизация в YouTube API."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(file_path, title, description):
    """Загружает видео на YouTube в формате Shorts."""
    youtube_service = authenticate_youtube()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['AI', 'Technology']
        },
        'status': {
            'privacyStatus': 'public'
        },
        'contentDetails': {
            'duration': 'PT60S',  # Указываем длительность видео (60 секунд для Shorts)
            'dimension': 'vertical',  # Указываем вертикальный формат (Shorts)
            'definition': 'hd'  # Указываем качество видео
        }
    }
    media = MediaFileUpload(file_path, mimetype='video/mp4')
    request = youtube_service.videos().insert(part='snippet,status,contentDetails', body=body, media_body=media)
    response = request.execute()
    print(f"Видео загружено: https://www.youtube.com/watch?v={response['id']}")
    return response['id']
