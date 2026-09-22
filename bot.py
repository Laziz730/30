import os
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN", "8946505099:AAF0ZCplo8whTLBZLEmRm39cE2UgabFqo1o")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@uzefpageshop")
WEB_URL = os.getenv("WEB_URL", "").rstrip("/")
PORT = int(os.getenv("PORT", 8000))

bot = telebot.TeleBot(BOT_TOKEN)


def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_search = types.KeyboardButton("🔍 Akkaunt qidirish")
    btn_add = types.KeyboardButton("➕ Elon berish")
    btn_my = types.KeyboardButton("📁 Elonlarim")
    btn_admin = types.KeyboardButton("👨‍💻 Adminlar")
    btn_rules = types.KeyboardButton("📚 Qoidalar")
    btn_prices = types.KeyboardButton("💰 Elon narxlari")

    # Tugmalarni qatorlarga joylashtirish
    markup.add(btn_search)           # to'liq kenglikdagi tugma
    markup.add(btn_add, btn_my)      # yonma-yon 2 ta
    markup.add(btn_admin, btn_rules) # yonma-yon 2 ta
    markup.add(btn_prices)           # to'liq kenglikdagi tugma
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
        # Oddiy e'lon kelganda kanalga joylash kodi
        user = message.from_user
        username = f"@{user.username}" if user.username else user.first_name

        bot.send_message(message.chat.id, "E'loningiz qabul qilindi, kanalga joylanmoqda...")

        if message.content_type == "photo":
            photo_id = message.photo[-1].file_id
            caption_text = f"{message.caption or ''}\n\n👤 **E'lon beruvchi:** {username}"
            bot.send_photo(CHANNEL_USERNAME, photo_id, caption=caption_text, parse_mode="Markdown")
        elif message.content_type == "text":
            full_text = f"{message.text}\n\n👤 E'lon beruvchi: {username}"
            bot.send_message(CHANNEL_USERNAME, full_text, parse_mode="Markdown")

        bot.send_message(message.chat.id, "✅ E'lon kanalga joylandi!", reply_markup=get_main_keyboard())


# ---------- Render uchun health server + keep-alive ----------

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
        self.wfile.write(b"\nBot ishlamoqda...")

    def log_message(self, *args):
        pass


def run_http():
    HTTPServer(("0.0.0.0", PORT), HealthHandler).serve_forever()


def keep_alive():
    # Har 5 daqiqada o'zini uyg'otib turadi (Render bekor uxlatmasligi uchun)
    while True:
        time.sleep(300)
        if WEB_URL:
            try:
                urllib.request.urlopen(WEB_URL + "/health", timeout=10)
            except Exception:
                pass


threading.Thread(target=run_http, daemon=True).start()
threading.Thread(target=keep_alive, daemon=True).start()

print("Bot ishlamoqda...")
bot.polling(none_stop=True)