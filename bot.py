import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ====== Настройки через env ======
BOT_TOKEN = os.environ.get("BOT_TOKEN")
LOG_CHAT_ID = int(os.environ.get("LOG_CHAT_ID", "0"))   # пример: -1001234567890 (для канала) или обычный chat id
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))         # твой Telegram ID (чтобы бот не слал лог о твоих проверках)
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").rstrip("/")  # https://your-service.onrender.com (без слэша в конце)
PORT = int(os.environ.get("PORT", "8000"))  # Render задаёт PORT автоматически во время выполнения. :contentReference[oaicite:4]{index=4}

if not BOT_TOKEN:
    raise SystemExit("Error: BOT_TOKEN environment variable is required.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    # Ответ пользователю
    if update.message:
        await update.message.reply_text(f"👋 Привет, {user.first_name or 'друг'}! Ты вошёл.")
    # Формируем лог (и шлём только если это не OWNER)
    if user.id != OWNER_ID and LOG_CHAT_ID:
        text = (
            f"📥 Новый вход:\n"
            f"🆔 ID: {user.id}\n"
            f"👤 Имя: {user.first_name or '—'}\n"
            f"💬 Username: @{user.username or '—'}\n"
            f"🕒 Время: {now}"
        )
        await context.bot.send_message(chat_id=LOG_CHAT_ID, text=text)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот живой")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))

    # Если задали WEBHOOK_URL — запускаем webhook (Render требует слушать порт из PORT). :contentReference[oaicite:5]{index=5}
    if WEBHOOK_URL:
        webhook_path = f"/webhook/{BOT_TOKEN}"  # уникальный путь
        full_webhook = f"{WEBHOOK_URL}{webhook_path}"
        print("Starting webhook. Listening on 0.0.0.0:%s, webhook url: %s" % (PORT, full_webhook))
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url_path=webhook_path,
            webhook_url=full_webhook
        )
    else:
        # Для локальной отладки — polling
        print("WEBHOOK_URL not set — starting polling (local mode)")
        app.run_polling()

if __name__ == "__main__":
    main()
