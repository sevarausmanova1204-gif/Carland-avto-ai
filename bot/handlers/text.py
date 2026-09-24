import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from .. import ai, analytics, db, keyboards
from .. import format as fmt
from ..i18n import t

logger = logging.getLogger(__name__)

# Botning ANCHA ESKI (aiogram'ga asoslangan, 16-sentabrgacha bo'lgan)
# versiyasi doimiy pastki klaviatura (ReplyKeyboardMarkup) yuborar edi.
# Telegram bunday klaviaturani bot maxsus ReplyKeyboardRemove yubormaguncha
# foydalanuvchi ekranida CHEKSIZ saqlab turadi — shu sabab hozirgi (inline
# tugmali) versiyaga o'tilgandan keyin ham, o'sha paytda botdan foydalangan
# odamlarning ilovasida bu eski tugmalar hali ko'rinib turishi mumkin edi.
# Bosilsa, matn oddiy xabar sifatida kelib, hech qanday rejimga to'g'ri
# kelmagani uchun AI chatga tushib, mavzuga aloqasi bo'lmagan javob
# qaytarardi (masalan "Biz haqimizda & Aloqa" so'zidagi "Biz" BIZOL moy
# brendiga tasodifan mos kelib ketgani kabi). Shu lug'at orqali bunday eski
# tugma matnini aniqlab, hozirgi ekvivalent bo'limga yo'naltiramiz va bir
# yo'la eski klaviaturani butunlay olib tashlaymiz.
_LEGACY_KEYBOARD_ACTIONS = {
    "🧮 Moy hisoblash": "oilcalc", "🧮 Подбор масла": "oilcalc", "🧮 Oil Calculator": "oilcalc",
    "📍 Carland filiallari": "branches", "📍 Филиалы Carland": "branches", "📍 Carland Branches": "branches",
    "🎁 Sentabr Aksiyalari": "promo", "🎁 Сентябрьские акции": "promo", "🎁 September Promos": "promo",
    "⚡ Tezkor narxlar": "products", "⚡ Экспресс цены": "products", "⚡ Quick Prices": "products",
    "💬 AI Maslahatchi": "ai", "💬 AI Консультант": "ai", "💬 AI Consultant": "ai",
    "📞 Biz haqimizda & Aloqa": "about", "📞 О нас и Контакты": "about", "📞 About & Contacts": "about",
    "🌐 Tilni o'zgartirish": "lang", "🌐 Сменить язык": "lang", "🌐 Change Language": "lang",
    "🧹 Suhbatni tozalash": "clear", "🧹 Очистить диалог": "clear", "🧹 Clear Chat": "clear",
}


async def _handle_legacy_button(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, lang: str):
    # Birinchi xabar HAR DOIM ReplyKeyboardRemove bilan yuboriladi — shu
    # bitta xabar eski klaviaturani doimiy olib tashlaydi (Telegram
    # tomonidan), qolgan barcha keyingi harakatlar esa hozirgi inline
    # menyu orqali davom etadi.
    await update.message.reply_text(t("legacy_keyboard_note", lang), reply_markup=ReplyKeyboardRemove())

    if action == "oilcalc":
        await update.message.reply_text(t("oilcalc_pick_brand", lang), reply_markup=keyboards.brand_grid("oilcalc", lang=lang))
    elif action == "branches":
        await update.message.reply_text(t("branches_pick_title", lang), reply_markup=keyboards.branches_menu(lang))
    elif action == "promo":
        await update.message.reply_text(t("promo_pick_brand", lang), reply_markup=keyboards.brand_grid("promo", lang=lang))
    elif action == "products":
        await update.message.reply_text(t("products_menu_title", lang), reply_markup=keyboards.products_category_menu(lang))
    elif action == "ai":
        context.user_data["mode"] = "ai"
        await update.message.reply_text(t("ai_mode_on", lang), reply_markup=keyboards.back_button(lang=lang))
    elif action == "about":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("menu_admin", lang), url=f"https://t.me/{keyboards.ADMIN_USERNAME}")],
            [InlineKeyboardButton(t("home_btn", lang), callback_data="menu:main")],
        ])
        await update.message.reply_text(t("about_text", lang), reply_markup=kb, parse_mode="Markdown")
    elif action == "lang":
        await update.message.reply_text(t("lang_pick", lang), reply_markup=keyboards.language_menu())
    elif action == "clear":
        recent_cars = context.user_data.get("recent_cars")
        context.user_data.clear()
        context.user_data["lang"] = lang
        if recent_cars:
            context.user_data["recent_cars"] = recent_cars
        await update.message.reply_text(
            t("cleared_text", lang),
            reply_markup=keyboards.main_menu(lang, has_recent=bool(recent_cars)),
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    text = update.message.text.strip()
    lang = context.user_data.get("lang", "uz")

    legacy_action = _LEGACY_KEYBOARD_ACTIONS.get(text)
    if legacy_action:
        analytics.log_event(update.effective_user, lang, "legacy_keyboard", legacy_action)
        await _handle_legacy_button(update, context, legacy_action, lang)
        return

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
