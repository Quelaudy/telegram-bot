import os
import requests

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

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
        return response.json()["choices"][0]["text"].strip()
    else:
        return topic
