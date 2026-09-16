import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from bot import config
from bot.handlers.callbacks import route
from bot.handlers.start import start
from bot.handlers.text import handle_text

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():
    if not config.TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN topilmadi. .env faylni to'ldiring (.env.example ga qarang).")

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(route))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logging.info("Carland bot ishga tushdi.")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
