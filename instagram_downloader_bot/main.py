import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import router


async def main():
    """
    Botni ishga tushiruvchi asosiy funksiya.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    if not BOT_TOKEN or BOT_TOKEN == "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ":
        logging.error("XATOLIK: BOT_TOKEN o'rnatilmagan! Iltimos, .env fayliga haqiqiy Telegram Bot tokeningizni kiriting.")
        print("\n" + "="*60)
        print("XATOLIK: BOT_TOKEN topilmadi!")
        print("1. Telegram'da @BotFather ga kiring va yangi bot oching.")
        print("2. Berilgan tokenni .env faylidagi BOT_TOKEN ga yozing:")
        print("   BOT_TOKEN=sizning_tokeningiz")
        print("="*60 + "\n")
        return

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ro'yxatdan o'tkazish
    dp.include_router(router)

    from ai_service import is_ai_configured
    if is_ai_configured():
        logging.info("Gemini AI xizmati muvaffaqiyatli ulandi.")
    else:
        logging.warning("DIQQAT: GEMINI_API_KEY o'rnatilmagan. AI funksiyalaridan to'liq foydalanish uchun .env ga GEMINI_API_KEY kiriting.")

    logging.info("Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda...")
    
    # Eski xabarlarni o'tkazib yuborish (drop_pending_updates=True)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")
