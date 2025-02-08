from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

import os

TOKEN = os.getenv("TOKEN")  # Используем переменную окружения

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Я Telegram-бот.")

async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    await update.message.reply_text(f"Ты сказал: {text}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен... Напиши /start в Telegram!")
    app.run_polling()

if __name__ == "__main__":
    main()
