import os
import requests
from search_video import search_video, download_video
from upload_to_drive import upload_to_google_drive
from post_to_youtube import upload_to_youtube

# Получаем API-ключ из переменной окружения
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

def generate_script(prompt):
    """Генерирует сценарий с помощью Together AI и ищет видео"""
    try:
        headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}"}
        json_data = {
            "model": "togethercomputer/llama-2-7b-chat",
            "prompt": f"Напиши сценарий для видео: {prompt}",
            "max_tokens": 200
        }

        response = requests.post("https://api.together.ai/v1/completions", headers=headers, json=json_data)

        if response.status_code == 200:
            script = response.json()["choices"][0]["text"].strip()
            print(f"[DEBUG] Сценарий сгенерирован: {script}")
            video_query = script
        else:
            print(f"[ERROR] Ошибка Together AI: {response.json()}")
            video_query = prompt
            script = prompt

    except Exception as e:
        print(f"[ERROR] Ошибка при запросе к Together AI: {e}")
        video_query = prompt
        script = prompt

    print(f"[DEBUG] Поиск видео по запросу: {video_query}")
    video_url = search_video(video_query)
    
    if not video_url:
        print("[ERROR] Видео не найдено.")
        return script, None

    print(f"[DEBUG] Найденное видео: {video_url}")
    download_video(video_url, "video.mp4")

    return script, video_url

if __name__ == "__main__":
    user_prompt = "Преимущества искусственного интеллекта"
    script, video_url = generate_script(user_prompt)

    if video_url:
        print("Загружаем видео на Google Диск...")
        drive_id = upload_to_google_drive("video.mp4", "uploaded_video.mp4")
        print(f"✅ Видео загружено на Google Диск: {drive_id}")

        print("Загружаем видео на YouTube...")
        youtube_id = upload_to_youtube("video.mp4", script, "Автоматически сгенерированное видео")
        print(f"✅ Видео опубликовано: https://www.youtube.com/watch?v={youtube_id}")
    else:
        print("❌ Видео не найдено, загрузка не выполнена.")
