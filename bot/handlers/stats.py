from telegram import Update
from telegram.ext import ContextTypes

from .. import analytics, config


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Faqat `ADMIN_IDS`dagi Telegram ID'lar uchun ishlaydi. Oddiy
    foydalanuvchiga hech qanday javob qaytarilmaydi — buyruq borligi ham
    bildirilmaydi. Ishlatilishi: /stats yoki /stats 30 (kunlar soni)."""
    user = update.effective_user
    if not user or user.id not in config.ADMIN_IDS:
        return
    days = 7
    if context.args and context.args[0].isdigit():
        days = max(1, min(90, int(context.args[0])))
    report = analytics.build_stats_report(days=days)
    await update.message.reply_text(report, parse_mode="Markdown")
