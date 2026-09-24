from telegram import ReplyKeyboardRemove, Update
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

    # Botning ancha eski versiyasidan qolgan doimiy pastki klaviatura
    # (ReplyKeyboardMarkup) ba'zi foydalanuvchilar ekranida hali ham
    # saqlanib qolgan bo'lishi mumkin (Telegram uni bot maxsus
    # ReplyKeyboardRemove yubormaguncha ko'rsatib turadi). Bitta
    # reply_markup faqat bitta turdagi klaviaturani ko'rsatishi mumkinligi
    # sabab, buni ALOHIDA (bo'sh) xabar bilan olib tashlaymiz, so'ng asosiy
    # xush kelibsiz xabari o'zining (inline) menyusi bilan yuboriladi.
    await update.message.reply_text(t("legacy_keyboard_note", lang), reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(
        t("welcome", lang),
        reply_markup=keyboards.main_menu(lang, has_recent=bool(recent_cars)),
        parse_mode="Markdown",
    )
