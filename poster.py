import os
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN", "8946505099:AAF0ZCplo8whTLBZLEmRm39cE2UgabFqo1o")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@uzefpageshop")

_bot = None


def get_bot():
    global _bot
    if _bot is None:
        _bot = telebot.TeleBot(BOT_TOKEN)
    return _bot


def post_elon(text, username, photo_path=None, photo_file_id=None, parse_mode=None):
    b = get_bot()
    footer = f"\n\n👤 E'lon beruvchi: {username}"
    caption = (text or "") + footer
    if photo_path:
        with open(photo_path, "rb") as f:
            b.send_photo(CHANNEL_USERNAME, f, caption=caption, parse_mode=parse_mode)
    elif photo_file_id:
        b.send_photo(CHANNEL_USERNAME, photo_file_id, caption=caption, parse_mode=parse_mode)
    else:
        b.send_message(CHANNEL_USERNAME, caption, parse_mode=parse_mode)