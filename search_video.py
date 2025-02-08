import requests
import random
import time

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")  

def search_video(query):
    """
    Ищет видео по запросу на Pexels, используя случайный выбор.
    :param query: Запрос для поиска видео.
    :return: Прямая ссылка на случайное видео или None, если видео не найдено.
    """
    # Добавляем случайный параметр в запрос, чтобы API давало разные результаты
    modified_query = f"{query} {random.randint(1, 1000)}"
    
    url = f"https://api.pexels.com/videos/search?query={modified_query}&per_page=10&sort=popular"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('videos'):
            # Выбираем случайное видео из списка
            random_video = random.choice(data['videos'])
            video_files = random_video['video_files']
            if video_files:
                best_video = max(video_files, key=lambda x: x.get('width', 0) * x.get('height', 0))
                video_url = best_video['link']
                print(f"[DEBUG] Выбрано случайное видео для запроса '{query}': {video_url}")
                return video_url
    else:
        print(f"[ERROR] Ошибка при запросе к Pexels API: {response.status_code} {response.text}")
    return None

def download_video(video_url, video_path):
    """
    Скачивает видео по прямой ссылке и сохраняет его в указанное место.
    :param video_url: Прямая ссылка на видео.
    :param video_path: Путь для сохранения видео.
    """
    if not video_url:
        print("[ERROR] Ошибка: ссылка на видео отсутствует.")
        return
    
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"[INFO] Видео сохранено как {video_path}")
    else:
        print("[ERROR] Ошибка загрузки видео")

# Пример использования
if __name__ == "__main__":
    query = input("Введите запрос для поиска видео: ")
    video_url = search_video(query)
    
    if video_url:
        download_video(video_url, "video.mp4")
    else:
        print("[ERROR] Видео не найдено.")
