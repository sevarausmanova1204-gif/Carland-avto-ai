"""
Carland AI Telegram Bot - Asosiy Ishga Tushirish Fayli (main.py)
aiogram 3.x asosida
"""

import asyncio
import logging
import sys
from pathlib import Path

# Joriy papkani sys.path ga qo'shish
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import router as main_router

# Loggingni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Botni ishga tushirish funksiyasi"""
    if not BOT_TOKEN:
        logger.error("XATOLIK: BOT_TOKEN ko'rsatilmagan! Iltimos, .env faylini to'ldiring.")
        return

    logger.info("Carland AI Telegram boti ishga tushirilmoqda...")

    # Bot va Dispatcher obyektlarini yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(main_router)

    # Eski kutilmagan update'larni tozalash va pollingni boshlash
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        bot_info = await bot.get_me()
        logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username} ({bot_info.first_name})")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
