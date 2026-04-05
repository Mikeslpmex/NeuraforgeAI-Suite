import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_BASE = os.getenv("API_BASE", "https://tu-api.onrender.com")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot de errores de NeuraforgeAI. Usa /errores")

async def errores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"{API_BASE}/frontend/errores/index.html"  # si sirves frontend desde la misma API
    keyboard = [[InlineKeyboardButton("Ver tabla", url=url)]]
    await update.message.reply_text("Tabla de errores:", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("errores", errores))
    app.run_polling()

if __name__ == "__main__":
    main()
