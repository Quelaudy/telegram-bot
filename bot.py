from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler, CallbackContext
import os
import datetime

from generate_script import generate_script_with_together_ai
from generate_speech import generate_speech_with_elevenlabs
from generate_video import generate_video_with_heygen
from upload_to_drive import upload_to_google_drive
from post_to_youtube import upload_to_youtube

TOKEN = os.getenv("TOKEN")

CHOOSING, ENTER_TEXT, ENTER_TITLE, ENTER_DESCRIPTION, CONFIRM_UPLOAD, ENTER_UPLOAD_DETAILS = range(6)

def get_greeting():
    hour = (datetime.datetime.utcnow().hour + 5) % 24  # Учитываем UTC+5
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

async def start(update: Update, context: CallbackContext) -> int:
    greeting = get_greeting()
    keyboard = [
        [InlineKeyboardButton("🎬 Сгенерировать сценарий", callback_data="generate")],
        [InlineKeyboardButton("✍ Написать свой сценарий", callback_data="manual")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"{greeting}! Вас приветствует телеграм-бот для генерации видео!\nВыберите действие:", reply_markup=reply_markup)
    return CHOOSING

async def help_command(update: Update, context: CallbackContext):
    greeting = get_greeting()
    await update.message.reply_text(f"{greeting}! Вас приветствует AI помощник! Чем могу Вам помочь?")

async def contacts_command(update: Update, context: CallbackContext):
    await update.message.reply_text("📞 Контакты владельца: example@email.com\n🔧 Сервисный центр: support@example.com")

async def choose_option(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Редактируем исходное сообщение, убираем кнопки
    if query.data == "generate":
        context.user_data["mode"] = "generate"
        await query.edit_message_text("Введите запрос для генерации сценария:", reply_markup=None)
    else:
        context.user_data["mode"] = "manual"
        await query.edit_message_text("Введите текст своего сценария:", reply_markup=None)

    return ENTER_TEXT

async def handle_text(update: Update, context: CallbackContext) -> int:
    text = update.message.text

    if context.user_data["mode"] == "generate":
        await update.message.reply_text("📝 Генерирую сценарий...")
        text = generate_script_with_together_ai(text)

    context.user_data["text"] = text
    keyboard = [
        [InlineKeyboardButton("✅ Оставить", callback_data="keep")],
        [InlineKeyboardButton("✍ Изменить", callback_data="edit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Сценарий:\n{text}\n\nХотите оставить или изменить?", reply_markup=reply_markup)
    return ENTER_TITLE

async def handle_title(update: Update, context: CallbackContext) -> int:
    context.user_data["title"] = update.message.text
    await update.message.reply_text("🔹 Введите описание для видео:")
    return ENTER_DESCRIPTION

async def handle_description(update: Update, context: CallbackContext) -> int:
    context.user_data["description"] = update.message.text
    keyboard = [[InlineKeyboardButton("✅ Подтвердить загрузку", callback_data="confirm_upload")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅ Видео готово к загрузке. Подтвердите загрузку на YouTube.", reply_markup=reply_markup)
    return CONFIRM_UPLOAD

async def confirm_upload(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("📅 Укажите дату и время публикации (формат: ГГГГ-ММ-ДД ЧЧ:ММ)", reply_markup=None)
    return ENTER_UPLOAD_DETAILS

async def enter_upload_details(update: Update, context: CallbackContext) -> int:
    context.user_data["upload_time"] = update.message.text
    title = context.user_data["title"]
    description = context.user_data["description"]
    text = context.user_data["text"]

    await update.message.reply_text("🎙️ Генерирую голос...")
    voice_path = generate_speech_with_elevenlabs(text)
    if not voice_path:
        await update.message.reply_text("❌ Ошибка генерации голоса!")
        return ConversationHandler.END

    await update.message.reply_text("🎥 Генерирую видео...")
    video_path = generate_video_with_heygen(text, voice_path)
    if not video_path:
        await update.message.reply_text("❌ Ошибка генерации видео!")
        return ConversationHandler.END

    await update.message.reply_text("☁️ Загружаю на Google Drive...")
    upload_to_google_drive(video_path, "generated_video.mp4")

    await update.message.reply_text("📺 Видео загружено!")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("contacts", contacts_command))

    # Добавляем обработчик для кнопок
    app.add_handler(CallbackQueryHandler(choose_option))

    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True, read_timeout=10, write_timeout=10, connect_timeout=10)

if __name__ == "__main__":
    main()
