import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from generate_script import generate_script
from search_video import search_video, download_video
from upload_to_drive import upload_to_google_drive
from post_to_youtube import upload_to_youtube

TOKEN = "7809744535:AAGtRvti_cG_A1ufCO-sMwY3f40oBuLhpsA"

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    update.message.reply_text("Привет! Отправь мне тему видео, и я его сгенерирую!")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Обрабатываем входящее сообщение"""
    text = update.message.text
    update.message.reply_text(f"⏳ Генерирую видео для темы: {text}...")

    # Генерируем сценарий и ищем видео
    script, video_url = generate_script(text)

    if not video_url:
        update.message.reply_text("❌ Видео не найдено.")
        return

    download_video(video_url, "video.mp4")
    update.message.reply_text("✅ Видео скачано, загружаем на Google Drive...")

    drive_id = upload_to_google_drive("video.mp4", "generated_video.mp4")
    update.message.reply_text(f"✅ Загружено на Google Drive (ID: {drive_id})")

    update.message.reply_text("🔹 Публикуем на YouTube...")
    youtube_id = upload_to_youtube("video.mp4", script, "Автоматическое видео")
    update.message.reply_text(f"✅ Видео опубликовано: https://www.youtube.com/watch?v={youtube_id}")

def main():
    """Запуск бота"""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
