import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
LOG_CHAT_ID = int(os.environ.get("LOG_CHAT_ID", "0"))
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").rstrip("/")
PORT = int(os.environ.get("PORT", "8000"))

if not BOT_TOKEN:
    raise SystemExit("Error: BOT_TOKEN environment variable is required.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    if update.message:
        await update.message.reply_text(f"👋 Привет, {user.first_name or 'друг'}! Ты вошёл.")

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

    if WEBHOOK_URL:
        full_webhook = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
        print(f"Starting webhook on port {PORT}, url: {full_webhook}")
        # Убираем webhook_url_path, слушаем корень /
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=full_webhook
        )
    else:
        print("WEBHOOK_URL not set — starting polling (local mode)")
        app.run_polling()


if __name__ == "__main__":
    main()
