import os
import openai
import re
from search_video import search_video, download_video
from upload_to_drive import upload_to_google_drive
from post_to_youtube import upload_to_youtube

def generate_script(prompt):
    try:
        os.getenv("OPENAI_API_KEY")
        response = openai.completions.create(
            model="gpt-4o-mini",
            prompt=prompt,
            max_tokens=200
        )
        script = response.choices[0].text.strip()
        print(f"[DEBUG] Сценарий сгенерирован: {script}")
        
        # Используем сценарий для поиска видео
        video_query = script  
    except Exception as e:
        print(f"[ERROR] Ошибка ChatGPT: {e}")
        video_query = input("ChatGPT недоступен. Введите тему для поиска видео: ")
        script = video_query  # Используем его же как сценарий

    print(f"[DEBUG] Поиск видео по запросу: {video_query}")

    # Выполняем поиск видео **один раз**
    video_url = search_video(video_query)
    if not video_url:
        print("[ERROR] Видео не найдено.")
        return script, None

    print(f"[DEBUG] Найденное видео: {video_url}")
    download_video(video_url, "video.mp4")

    return script, video_url

if __name__ == "__main__":
    user_prompt = "Напиши сценарий для видео о преимуществах искусственного интеллекта."
    script, video_url = generate_script(user_prompt)

    if video_url:
        print("Загружаем видео на Google Диск...")
        drive_id = upload_to_google_drive("video.mp4", "uploaded_video.mp4")
        print(f"Видео загружено на Google Диск с ID: {drive_id}")

        print("Загружаем видео на YouTube...")
        youtube_id = upload_to_youtube("video.mp4", script, "Автоматически сгенерированное видео")
        print(f"Видео опубликовано: https://www.youtube.com/watch?v={youtube_id}")
    else:
        print("Видео не найдено, загрузка не выполнена.")
