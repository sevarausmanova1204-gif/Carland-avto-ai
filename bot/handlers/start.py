from telegram import Update
from telegram.ext import ContextTypes

from .. import analytics, keyboards
from ..i18n import t


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    # "So'nggi ko'rilgan mashinalar" ro'yxati ham `lang` kabi /start bosilganda
    # SAQLANIB qolishi kerak — aks holda foydalanuvchi botni qayta ishga
    # tushirgan sayin (masalan chalkashib qolib /start bosganda) tarixi
    # yo'qolib, funksiya deyarli foydasiz bo'lib qolardi.
    recent_cars = context.user_data.get("recent_cars")
    context.user_data.clear()
    context.user_data["lang"] = lang
    if recent_cars:
        context.user_data["recent_cars"] = recent_cars
    analytics.log_event(update.effective_user, lang, "start")
    await update.message.reply_text(
        t("welcome", lang),
        reply_markup=keyboards.main_menu(lang, has_recent=bool(recent_cars)),
        parse_mode="Markdown",
    )
