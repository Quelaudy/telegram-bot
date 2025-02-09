from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler, CallbackContext
import os

from generate_script import generate_script_with_together_ai
from generate_speech import generate_speech_with_elevenlabs
from generate_video import generate_video_with_heygen
from upload_to_drive import upload_to_google_drive
from post_to_youtube import upload_to_youtube

TOKEN = os.getenv("TOKEN")

CHOOSING, ENTER_TEXT, ENTER_TITLE, ENTER_DESCRIPTION = range(4)

async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("🔹 Сгенерировать текст", callback_data="generate")],
        [InlineKeyboardButton("✍ Ввести текст вручную", callback_data="manual")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите способ создания текста:", reply_markup=reply_markup)
    return CHOOSING

async def choose_option(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "generate":
        context.user_data["mode"] = "generate"
        await query.edit_message_text("Введите тему видео:")
    else:
        context.user_data["mode"] = "manual"
        await query.edit_message_text("Введите полный текст для видео:")

    return ENTER_TEXT

async def handle_text(update: Update, context: CallbackContext) -> int:
    text = update.message.text

    if context.user_data["mode"] == "generate":
        await update.message.reply_text("📝 Генерирую сценарий через Together AI...")
        text = generate_script_with_together_ai(text)

    context.user_data["text"] = text
    await update.message.reply_text("🔹 Введите заголовок для видео:")
    return ENTER_TITLE

async def handle_title(update: Update, context: CallbackContext) -> int:
    context.user_data["title"] = update.message.text
    await update.message.reply_text("🔹 Введите описание для видео:")
    return ENTER_DESCRIPTION

async def handle_description(update: Update, context: CallbackContext) -> int:
    context.user_data["description"] = update.message.text
    text = context.user_data["text"]
    title = context.user_data["title"]
    description = context.user_data["description"]

    print(f"[DEBUG] Текст для генерации голоса: {text}", flush=True)

    await update.message.reply_text("🎙️ Генерирую голос через ElevenLabs...")
    
    voice_path = generate_speech_with_elevenlabs(text)

    if not voice_path:
        error_msg = "❌ Ошибка генерации голоса! Проверь логи."
        print(f"[ERROR] {error_msg}", flush=True)
        await update.message.reply_text(error_msg)
        return ConversationHandler.END

    print(f"[DEBUG] Файл сгенерированного голоса: {voice_path}", flush=True)

    await update.message.reply_text("🎥 Генерирую видео через HeyGen...")
    video_path = generate_video_with_heygen(text, voice_path)

    if not video_path:
        error_msg = "❌ Ошибка генерации видео!"
        print(f"[ERROR] {error_msg}", flush=True)
        await update.message.reply_text(error_msg)
        return ConversationHandler.END

    await update.message.reply_text("☁️ Загружаю на Google Drive...")
    drive_id = upload_to_google_drive(video_path, "generated_video.mp4")

    await update.message.reply_text("📺 Загружаю на YouTube...")
    youtube_id = upload_to_youtube(video_path, title, description)
    youtube_link = f"https://www.youtube.com/watch?v={youtube_id}"

    await update.message.reply_text(f"✅ Видео загружено!\n📺 YouTube: {youtube_link}")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [CallbackQueryHandler(choose_option, per_message=True)],
            ENTER_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            ENTER_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)],
            ENTER_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description)]
        },
        fallbacks=[],
        per_message=True
    )

    app.add_handler(conv_handler)
    print("✅ Бот запущен...", flush=True)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
