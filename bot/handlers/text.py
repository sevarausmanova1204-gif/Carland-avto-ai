import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from .. import ai, analytics, db, keyboards
from .. import format as fmt
from ..i18n import t

logger = logging.getLogger(__name__)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    text = update.message.text.strip()
    lang = context.user_data.get("lang", "uz")

    if mode == "oilsearch":
        kind = context.user_data.get("oilsearch_kind", "motor")
        car_id = context.user_data.get("oilsearch_car_id")
        analytics.log_event(update.effective_user, lang, "oil_search_query", text)
        results = db.search_oil_by_name(text, kind)
        reply_text = fmt.oil_search_results_text(text, results, lang)
        kb = keyboards.back_button(f"oilprice:{kind}:{car_id}" if car_id else "menu:main", lang=lang)
        await update.message.reply_text(reply_text, reply_markup=kb, parse_mode="Markdown")
        return

    if mode == "search":
        purpose = context.user_data.get("search_purpose", "oilcalc")
        extra = context.user_data.get("search_extra")
        analytics.log_event(update.effective_user, lang, "search_query", text)
        results = db.search_cars(text, limit=10)
        if not results:
            await update.message.reply_text(
                t("search_no_results", lang),
                reply_markup=keyboards.back_button(lang=lang),
            )
            return
        rows = []
        for r in results:
            cb = f"car:{purpose}:{r['id']}" + (f":{extra}" if extra else "")
            rows.append([InlineKeyboardButton(r["model"], callback_data=cb)])
        rows.append([InlineKeyboardButton(t("home_btn", lang), callback_data="menu:main")])
        await update.message.reply_text(t("search_results_title", lang), reply_markup=InlineKeyboardMarkup(rows))
        return

    # Boshqa hech qanday rejim tanlanmagan bo'lsa ham, foydalanuvchi shunchaki
    # savol yozgan bo'lishi mumkin — shu sabab har doim AI orqali javob
    # beramiz (faqat "search" rejimi alohida ushlab qolinadi, yuqorida).
    analytics.log_event(update.effective_user, lang, "ai_chat", text)
    await update.message.chat.send_action(ChatAction.TYPING)
    thinking = await update.message.reply_text(t("ai_thinking", lang))
    keyboard_kind = None
    try:
        answer, keyboard_kind = await ai.ask_ai(text, context)
    except Exception:  # noqa: BLE001
        # Xato tafsilotini (API kaliti, provayder xatoligi va h.k.) mijozga
        # ko'rsatmaymiz — faqat serverga log qilamiz, mijozga umumiy va
        # xavfsiz xabar beriladi.
        logger.exception("AI so'roviga javob berishda xatolik (matn: %r)", text)
        answer = t("ai_error", lang)

    if keyboard_kind == "branches":
        # Filial/manzil so'ralganda javob ostida to'g'ridan-to'g'ri TANLASH
        # mumkin bo'lgan filiallar ro'yxati chiqadi — foydalanuvchi "bosh
        # menyudan qidiring" deb alohida yo'naltirilmasdan, shu yerning
        # o'zida filialni bosib, lokatsiyasini (GPS) olishi mumkin.
        reply_markup = keyboards.branches_menu(lang)
    else:
        has_recent = bool(context.user_data.get("recent_cars"))
        reply_markup = keyboards.main_menu(lang, has_recent=has_recent)

    try:
        await thinking.edit_text(answer, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:  # noqa: BLE001
        # Erkin AI (LLM) javobi ba'zan Telegram Markdown qoidalariga mos
        # kelmaydigan belgilar (masalan juftlanmagan * yoki _) qaytarishi
        # mumkin — bunday holda Markdown butunlay rad etilib, foydalanuvchi
        # HECH QANDAY javob olmasdan qolib ketmasligi uchun oddiy matn
        # sifatida qayta yuboramiz.
        await thinking.edit_text(answer, reply_markup=reply_markup)
