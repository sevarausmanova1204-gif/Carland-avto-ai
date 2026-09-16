from telegram import Update
from telegram.ext import ContextTypes

from .. import keyboards
from ..i18n import t


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    context.user_data.clear()
    context.user_data["lang"] = lang
    await update.message.reply_text(t("welcome", lang), reply_markup=keyboards.main_menu(lang), parse_mode="Markdown")
