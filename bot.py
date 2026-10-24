import os
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
)

# Загружаем секреты из файла .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "user.json"

def load_data():
    """Читаем профили с диска. Если файла еще нет, начинаем с пустого словаря."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    """Записываем ВЕСЬ словарь в файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_data = load_data()  # загружаем один раз при старте бота

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid in user_data:
        name = user_data[uid]["name"]
        sport = user_data[uid].get("sport", "не выбран")
        await update.message.reply_text(f"С возвращением, {name}! Твой спорт: {sport}")
    else:
        await update.message.reply_text("Привет! Как тебя зовут?")

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    name = update.message.text

    user_data[uid] = {"name": name}
    save_data(user_data)

    # Разбили кнопки по 2 в ряд, чтобы текст красиво помещался на экране телефона
    buttons = [
        [
            InlineKeyboardButton("Футбол", callback_data="футбол"),
            InlineKeyboardButton("Баскетбол", callback_data="баскетбол"),
        ],
        [
            InlineKeyboardButton("Теннис", callback_data="теннис"),
            InlineKeyboardButton("Хоккей", callback_data="хоккей"),
        ],
        [
            InlineKeyboardButton("Плавание", callback_data="плавание"),
            InlineKeyboardButton("Настольный теннис", callback_data="настольный теннис"),
        ],
        [
            InlineKeyboardButton("Киберспорт", callback_data="киберспорт"),
        ],
    ]
    await update.message.reply_text(
        f"Приятно познакомиться, {name}! Какой твой любимый вид спорта?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def pick_sport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)

    if uid not in user_data:
        user_data[uid] = {"name": query.from_user.first_name}

    user_data[uid]["sport"] = query.data
    save_data(user_data)

    await query.edit_message_text(f"Запомнил: любимый спорт — {query.data}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(pick_sport))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_name))

app.run_polling()