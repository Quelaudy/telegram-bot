import os
import requests

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def generate_speech_with_elevenlabs(text, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """Генерирует аудио с ElevenLabs"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    json_data = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }

    response = requests.post(url, headers=headers, json=json_data)

    if response.status_code == 200:
        audio_path = "generated_voice.mp3"
        with open(audio_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Аудио сохранено: {audio_path}")
        return audio_path
    else:
        print("[ERROR] Ошибка генерации голоса:", response.status_code, response.text)
        return None
