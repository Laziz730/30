import os

import telebot
from telebot import types

import poster

BOT_TOKEN = os.getenv("BOT_TOKEN", "8946505099:AAF0ZCplo8whTLBZLEmRm39cE2UgabFqo1o")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@uzefpageshop")
WEB_URL = os.getenv("WEB_URL", "").rstrip("/")

bot = telebot.TeleBot(BOT_TOKEN)


def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_search = types.KeyboardButton("🔍 Akkaunt qidirish")
    btn_add = types.KeyboardButton("➕ Elon berish")
    btn_my = types.KeyboardButton("📁 Elonlarim")
    btn_admin = types.KeyboardButton("👨‍💻 Adminlar")
    btn_rules = types.KeyboardButton("📚 Qoidalar")
    btn_prices = types.KeyboardButton("💰 Elon narxlari")

    markup.add(btn_search)
    markup.add(btn_add, btn_my)
    markup.add(btn_admin, btn_rules)
    markup.add(btn_prices)
    return markup


@bot.message_handler(commands=["start"])
def start_message(message):
    text = (
        "Assalomu aleykum @uzefpageshop avto e'lon yuboruvchi botiga xush kelibsiz!\n\n"
        "Rasmiy sahifalarimiz:\n"
        "@uzefpage\n"
        "@uzefpageshop\n"
        "Coins donat xizmati:\n"
        "@uzefpagecoins"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())
    if WEB_URL:
        web_kb = types.InlineKeyboardMarkup()
        web_kb.add(types.InlineKeyboardButton("🌐 Saytda e'lon berish", url=WEB_URL + "/post"))
        bot.send_message(message.chat.id, "Sayt orqali ham e'lon bera olasiz:", reply_markup=web_kb)


@bot.message_handler(content_types=["text", "photo"])
def handle_ad(message):
    if message.text == "🔍 Akkaunt qidirish":
        bot.send_message(message.chat.id, "🔍 Qidirayotgan akkauntingiz haqida ma'lumot kiriting:")
    elif message.text == "➕ Elon berish":
        bot.send_message(message.chat.id, "E'lon matnini yoki rasmini yuboring, men uni kanalga joylayman.")
    elif message.text == "📁 Elonlarim":
        bot.send_message(message.chat.id, "📁 Sizning e'lonlaringiz ro'yxati:")
    elif message.text == "👨‍💻 Adminlar":
        bot.send_message(message.chat.id, "👨‍💻 Admin bilan bog'lanish: @kadirvss")
    elif message.text == "📚 Qoidalar":
        bot.send_message(message.chat.id, "📚 Qoidalar bilan tanishib chiqing...")
    elif message.text == "💰 Elon narxlari":
        bot.send_message(message.chat.id, "💰 E'lon berish narxlari ro'yxati...")
    else:
        user = message.from_user
        username = f"@{user.username}" if user.username else user.first_name

        bot.send_message(message.chat.id, "E'loningiz qabul qilindi, kanalga joylanmoqda...")

        try:
            if message.content_type == "photo":
                photo_id = message.photo[-1].file_id
                poster.post_elon(message.caption or "", username, photo_file_id=photo_id)
            elif message.content_type == "text":
                poster.post_elon(message.text, username)
            bot.send_message(message.chat.id, "✅ E'lon kanalga joylandi!", reply_markup=get_main_keyboard())
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Xato: {e}", reply_markup=get_main_keyboard())

def process_update(update_json):
    update = telebot.types.Update.de_json(update_json)
    bot.process_new_updates([update])