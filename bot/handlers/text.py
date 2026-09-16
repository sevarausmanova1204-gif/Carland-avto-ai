from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .. import ai, db, keyboards
from .. import format as fmt


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    text = update.message.text.strip()

    if mode == "oilsearch":
        kind = context.user_data.get("oilsearch_kind", "motor")
        car_id = context.user_data.get("oilsearch_car_id")
        results = db.search_oil_by_name(text, kind)
        reply_text = fmt.oil_search_results_text(text, results)
        kb = keyboards.back_button(f"oilprice:{kind}:{car_id}" if car_id else "menu:main")
        await update.message.reply_text(reply_text, reply_markup=kb, parse_mode="Markdown")
        return

    if mode == "search":
        purpose = context.user_data.get("search_purpose", "oilcalc")
        extra = context.user_data.get("search_extra")
        results = db.search_cars(text, limit=10)
        if not results:
            await update.message.reply_text(
                "Hech narsa topilmadi. Qayta urinib ko'ring yoki menyudan tanlang.",
                reply_markup=keyboards.back_button(),
            )
            return
        rows = []
        for r in results:
            cb = f"car:{purpose}:{r['id']}" + (f":{extra}" if extra else "")
            rows.append([InlineKeyboardButton(r["model"], callback_data=cb)])
        rows.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu:main")])
        await update.message.reply_text("Topilgan natijalar:", reply_markup=InlineKeyboardMarkup(rows))
        return

    # Boshqa hech qanday rejim tanlanmagan bo'lsa ham, foydalanuvchi shunchaki
    # savol yozgan bo'lishi mumkin — shu sabab har doim AI orqali javob
    # beramiz (faqat "search" rejimi alohida ushlab qolinadi, yuqorida).
    thinking = await update.message.reply_text("💭 O'ylayapman...")
    try:
        answer = await ai.ask_ai(text)
    except Exception as e:  # noqa: BLE001
        answer = f"AI xizmatida xatolik yuz berdi: {e}"
    await thinking.edit_text(answer, reply_markup=keyboards.main_menu(context.user_data.get("lang", "uz")))
