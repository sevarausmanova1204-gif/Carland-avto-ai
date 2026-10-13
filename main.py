import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

from bot import config
from bot.handlers.callbacks import route
from bot.handlers.start import aksiya_command, keshbek_command, start
from bot.handlers.stats import stats_command
from bot.handlers.text import handle_text

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# httpx har bir so'rovning to'liq URL'ini (ichida bot TOKENI bor) INFO darajada logga
# yozadi — token Railway loglarida ochiq ko'rinib qolmasligi uchun faqat ogohlantirish va xatolar.
for _noisy in ("httpx", "httpcore"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)


def main():
    if not config.TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN topilmadi. .env faylni to'ldiring (.env.example ga qarang).")

    # PicklePersistence: foydalanuvchi tili va suhbat konteksti (masalan
    # oxirgi so'ralgan mashina) endi diskka yoziladi va bot qayta ishga
    # tushganda (deploy/restart) qayta o'qib olinadi — shu bilan "til
    # rus tiliga o'tkazilgandan keyin ba'zi ekranlar yana o'zbekchada
    # chiqib qolishi" muammosi (sabab: bot qayta ishga tushganda hamma
    # foydalanuvchining tili operativ xotiradan o'chib, standart "uz"ga
    # qaytib ketardi) butunlay bartaraf etiladi.
    persistence = PicklePersistence(filepath=str(config.PERSISTENCE_PATH))
    async def _post_init(application):
        # Telegram "Menyu" tugmasidagi buyruqlar ro'yxati
        from telegram import BotCommand

        try:
            await application.bot.set_my_commands([
                BotCommand("start", "Boshlash / Главное меню"),
                BotCommand("keshbek", "5% keshbek — qanday olinadi"),
                BotCommand("aksiya", "Aksiyalar va sovg'alar"),
            ])
        except Exception:  # noqa: BLE001
            logging.exception("Buyruqlar ro'yxatini o'rnatib bo'lmadi")

    app = (
        Application.builder().token(config.TELEGRAM_BOT_TOKEN).persistence(persistence).post_init(_post_init).build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("keshbek", keshbek_command))
    app.add_handler(CommandHandler("aksiya", aksiya_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(route))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logging.info("Carland bot ishga tushdi.")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
