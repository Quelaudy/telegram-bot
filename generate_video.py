import os
import requests

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

def generate_video_with_heygen(script_text, voice_path):
    """Создает видео с HeyGen"""
    if not os.path.exists(voice_path):
        print(f"[ERROR] Файл {voice_path} не найден!")
        return None

    url = "https://api.heygen.com/v1/video/generate"
    headers = {"Authorization": f"Bearer {HEYGEN_API_KEY}"}

    files = {"voice_file": open(voice_path, "rb")}

    json_data = {
        "text": script_text,
        "avatar": "your_avatar_id_here"
    }

    response = requests.post(url, headers=headers, json=json_data, files=files)

    if response.status_code == 200:
        video_url = response.json().get("video_url")
        video_path = "generated_video.mp4"
        return video_path
    else:
        print(f"[ERROR] Ошибка генерации видео: {response.status_code} {response.text}")
        return None
