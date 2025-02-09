import os
import requests

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def log_error(message):
    with open("bot_errors.log", "a") as f:
        f.write(message + "\n")

def generate_speech_with_elevenlabs(text, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """Генерирует аудио с ElevenLabs"""
    
    if not ELEVENLABS_API_KEY:
        error_msg = "[ERROR] API-ключ ElevenLabs отсутствует!"
        print(error_msg, flush=True)
        log_error(error_msg)
        return None

    if not text.strip():
        error_msg = "[ERROR] Передан пустой текст для генерации голоса!"
        print(error_msg, flush=True)
        log_error(error_msg)
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    
    json_data = {"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}

    print(f"[DEBUG] Отправляю запрос в ElevenLabs: {json_data}", flush=True)

    response = requests.post(url, headers=headers, json=json_data)

    if response.status_code == 200:
        audio_path = "generated_voice.mp3"
        with open(audio_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Аудиофайл сохранен: {audio_path}", flush=True)
       
