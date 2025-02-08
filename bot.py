from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os

# ✅ Импортируем автоматизированную систему
from generate_script import generate_script
from search_video import search_video, download_video
from upload_to_drive import upload_to_google_drive
from post_to_youtube import upload_to_youtube

TOKEN = os.getenv("TOKEN")  # Получаем токен бота из переменной окружения

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Отправь мне тему видео, и я его создам!")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Получает сообщение от пользователя и запускает автоматизированную систему"""
    topic = update.message.text
    await update.message.reply_text(f"⏳ Создаю видео на тему: {topic}...")

    # ✅ Генерируем сценарий
    script, video_url = generate_script(topic)
    if not video_url:
        await update.message.reply_text("❌ Видео не найдено!")
        return

    await update.message.reply_text("🎬 Видео найдено, скачиваю...")
    download_video(video_url, "video.mp4")

    await update.message.reply_text("☁️ Загружаю на Google Drive...")
    drive_id = upload_to_google_drive("video.mp4", "generated_video.mp4")

    await update.message.reply_text("📺 Загружаю на YouTube...")
    youtube_id = upload_to_youtube("video.mp4", script, topic)
    youtube_link = f"https://www.youtube.com/watch?v={youtube_id}"

    await update.message.reply_text(f"✅ Видео загружено!\n📺 YouTube: {youtube_link}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен... Напиши тему видео в Telegram!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Бот работает!", 200  # Ответ для UptimeRobot

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Flask слушает на порту 10000
