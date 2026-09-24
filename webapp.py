import os
import sqlite3
import time
from datetime import datetime

import telebot
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session

import poster
import bot_handlers

BASE = "/tmp" if os.getenv("VERCEL") else os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "elons.db")
UPLOAD_DIR = os.path.join(BASE, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "changeme123")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8946505099:AAF0ZCplo8whTLBZLEmRm39cE2UgabFqo1o")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret-key")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

CATEGORIES = [
    "🛒 Sotaman",
    "🔍 Qidiraman",
    "💼 Xizmat",
    "🏠 Ko'chmas mulk",
    "🚗 Avtomobil",
    "👕 Kiyim",
    "📱 Elektronika",
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS elons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            price TEXT,
            text TEXT,
            photo TEXT,
            username TEXT,
            phone TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/health")
def health():
    return "OK"


@app.route("/api/cron")
def cron():
    # Vercel Cron — har 5 daqiqada ishga tushib, bot'ni faol ushlab turadi
    import urllib.request
    url = os.getenv("WEB_URL", "").rstrip("/")
    if url:
        try:
            urllib.request.urlopen(url + "/health", timeout=10)
        except Exception:
            pass
    return "OK"


@app.route("/api/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    if not update:
        return "bad", 400
    try:
        bot_handlers.process_update(update)
    except Exception as e:
        return str(e), 500
    return "OK"


@app.route("/")
def index():
    conn = get_db()
    items = conn.execute("SELECT * FROM elons ORDER BY id DESC").fetchall()
    conn.close()
    cat = request.args.get("cat", "")
    if cat:
        items = [i for i in items if i["category"] == cat]
    return render_template("index.html", items=items, categories=CATEGORIES, cat=cat)


@app.route("/post", methods=["GET", "POST"])
def post_elon_page():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        price = request.form.get("price", "").strip()
        text = request.form.get("text", "").strip()
        username = request.form.get("username", "").strip()
        phone = request.form.get("phone", "").strip()

        photo_file = request.files.get("photo")
        photo_path = None
        if photo_file and photo_file.filename:
            photo_path = os.path.join(UPLOAD_DIR, f"{int(time.time())}_{photo_file.filename}")
            photo_file.save(photo_path)

        if not title and not text:
            flash("Kamida matn yoki sarlavha kiriting", "error")
            return redirect(url_for("post_elon_page"))

        body = "\n".join(x for x in [
            f"🏷 {title}" if title else "",
            f"📁 {category}" if category else "",
            f"💰 {price}" if price else "",
            f"☎️ {phone}" if phone else "",
            text,
        ] if x)

        try:
            poster.post_elon(body, username or "anonim", photo_path=photo_path)
        except Exception as e:
            flash(f"Kanalga yuborishda xato: {e}", "error")

        conn = get_db()
        conn.execute(
            "INSERT INTO elons (title, category, price, text, photo, username, phone, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (title, category, price, text,
             ("uploads/" + os.path.basename(photo_path)) if photo_path else None,
             username, phone, datetime.now().strftime("%d.%m.%Y %H:%M")),
        )
        conn.commit()
        conn.close()

        flash("✅ E'loningiz qabul qilindi va kanalga joylandi!", "ok")
        return redirect(url_for("index"))

    return render_template("post.html", categories=CATEGORIES)


@app.route("/uploads/<path:name>")
def uploads(name):
    return send_from_directory(UPLOAD_DIR, name)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        u = request.form.get("user", "")
        p = request.form.get("pass", "")
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["admin"] = True
            flash("✅ Kirish muvaffaqiyatli", "ok")
            return redirect(url_for("admin"))
        else:
            flash("❌ Noto'g'ri login yoki parol", "error")

    if not session.get("admin"):
        return render_template("admin_login.html")

    conn = get_db()
    items = conn.execute("SELECT * FROM elons ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin.html", items=items)


@app.route("/admin/delete/<int:eid>", methods=["POST"])
def admin_delete(eid):
    if not session.get("admin"):
        return redirect(url_for("admin"))
    conn = get_db()
    row = conn.execute("SELECT photo FROM elons WHERE id = ?", (eid,)).fetchone()
    if row and row["photo"]:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), row["photo"].replace("/", os.sep))
        if os.path.exists(p):
            os.remove(p)
    conn.execute("DELETE FROM elons WHERE id = ?", (eid,))
    conn.commit()
    conn.close()
    flash("🗑 O'chirildi", "ok")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))