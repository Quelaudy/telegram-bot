import os
import requests

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")

def generate_script_with_together_ai(topic):
    """Генерирует сценарий с помощью Together AI"""
    url = "https://api.together.ai/v1/completions"
    headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}"}
    json_data = {
        "model": "togethercomputer/llama-2-7b-chat",
        "prompt": f"Напиши подробный сценарий для видео на тему: {topic}",
        "max_tokens": 200
    }

    response = requests.post(url, headers=headers, json=json_data)

    if response.status_code == 200:
        script = response.json()["choices"][0]["text"].strip()
        print(f"[INFO] Сценарий создан: {script}")
        return script
    else:
        print(f"[ERROR] Ошибка Together AI: {response.json()}")
        return topic  # Если ошибка, используем введенную тему как текст

def generate_video_with_heygen(script_text):
    """Создает видео с HeyGen"""
    url = "https://api.heygen.com/v1/video/generate"
    headers = {"Authorization": f"Bearer {HEYGEN_API_KEY}", "Content-Type": "application/json"}
    
    json_data = {
        "text": script_text,
        "voice": "en_female_1",
        "avatar": "ai_avatar_1"
    }

    response = requests.post(url, headers=headers, json=json_data)
    
    if response.status_code == 200:
        video_url = response.json().get("video_url")
        video_path = "generated_video.mp4"
        download_video(video_url, video_path)
        return video_path
    else:
        print("[ERROR] Ошибка генерации видео:", response.text)
        return None

def download_video(url, filename):
    """Скачивает видео"""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"✅ Видео сохранено: {filename}")
    else:
        print("[ERROR] Ошибка скачивания видео")
