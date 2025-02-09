from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, CallbackContext
import os
from generate_script import generate_video_with_heygen
from upload_to_drive import upload_to_google_drive
from post_to_youtube import upload_to_youtube

TOKEN = os.getenv("TOKEN")  # Получаем токен бота из переменной окружения

# Состояния диалога
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

    await update.message.reply_text("🎥 Генерирую видео через HeyGen...")
    video_path = generate_video_with_heygen(text)

    if not video_path:
        await update.message.reply_text("❌ Ошибка генерации видео!")
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
            CHOOSING: [CallbackQueryHandler(choose_option)],
            ENTER_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
            ENTER_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)],
            ENTER_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description)]
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    print("✅ Бот запущен...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
