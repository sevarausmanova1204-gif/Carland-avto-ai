# pyright: reportOptionalMemberAccess=false, reportAttributeAccessIssue=false, reportArgumentType=false
"""
Carland Telegram Bot - Xabarlar va Hodisalarni Boshqarish (Handlers)
aiogram 3.x asosida
O'zbekcha (uz), Ruscha (ru), Inglizcha (en) to'liq qo'llab-quvvatlanadi.
"""

import asyncio
import logging
import time
from typing import Optional
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.chat_action import ChatActionSender

from user_language import get_user_lang, set_user_lang
from car_data import CARS_DATABASE, find_car_by_query, DUAL_TRANSMISSION_CARS
from carland_knowledge import CARLAND_BRANCHES, POPULAR_OILS, GM_SVECHALAR_PRICING, SEPTEMBER_AKSIYALAR
from calculator import format_car_oil_report
from smart_intent import resolve_smart_intent, is_direct_question
from infographics import generate_vehicle_infographic
from ai_service import (
    get_gemini_response,
    clear_user_chat_history,
    get_fallback_answer,
    get_fast_direct_answer,
    smart_automotive_answer,
    answer_automotive_question
)
from keyboards import (
    get_language_inline_keyboard,
    get_main_keyboard,
    get_brands_inline_keyboard,
    get_cars_inline_keyboard,
    get_car_result_keyboard,
    get_branches_links_keyboard,
    get_transmission_keyboard,
    get_about_keyboard,
    get_infographic_nav_keyboard
)

logger = logging.getLogger(__name__)
router = Router()


async def safe_send_message(
    message: Message,
    text: str,
    parse_mode: Optional[str] = "HTML",
    reply_markup=None,
    disable_web_page_preview: bool = True
):
    """
    Xabarni 100% ishonchli va xavfsiz yetkazish.
    Agar Telegram HTML parse xatosi bersa, xabar yo'qolib ketmasligi uchun darhol parse_mode=None bilan qayta yuboradi.
    4000 belgidan oshsa, avtomatik ravishda qismlarga bo'ladi.
    """
    if not text:
        return None

    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)] if len(text) > 4000 else [text]
    last_msg = None
    for idx, chunk in enumerate(chunks):
        current_markup = reply_markup if idx == len(chunks) - 1 else None
        try:
            last_msg = await message.answer(
                chunk,
                parse_mode=parse_mode,
                reply_markup=current_markup,
                disable_web_page_preview=disable_web_page_preview
            )
        except Exception as e:
            logger.warning(f"parse_mode={parse_mode} bilan yuborishda xatolik ({e}), parse_mode=None bilan qayta yuborilmoqda")
            try:
                last_msg = await message.answer(
                    chunk,
                    parse_mode=None,
                    reply_markup=current_markup,
                    disable_web_page_preview=disable_web_page_preview
                )
            except Exception as err2:
                logger.error(f"Xabar yuborishda yakuniy xatolik: {err2}")
    return last_msg


async def safe_edit_message(
    call: CallbackQuery,
    text: str,
    parse_mode: Optional[str] = "HTML",
    reply_markup=None
):
    """Inline xabarni xavfsiz tahrirlash (message is not modified xatolarini ushlab qoladi)"""
    if not call.message or not isinstance(call.message, Message):
        return
    try:
        await call.message.edit_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        if "message is not modified" in str(e).lower():
            return
        try:
            await call.message.edit_text(text, parse_mode=None, reply_markup=reply_markup)
        except Exception:
            pass


# === BUYRUQLAR (COMMANDS) ===

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Start buyrug'i handleri - Til tanlash taklifi va Asosiy Menyu tugmalari"""
    user_name = message.from_user.full_name if message.from_user else "Hurmatli mijoz"
    user_id = message.from_user.id if message.from_user else 0
    lang = get_user_lang(user_id)
    
    start_text = (
        f"Assalomu alaykum, <b>{user_name}</b>! 👋\n"
        "🚗 <b>Carland</b> rasmiy botiga xush kelibsiz!\n"
        "Iltimos, o'zingizga qulay tilni tanlang:\n\n"
        "Здравствуйте! 👋\n"
        "Добро пожаловать в официальный бот <b>Carland</b>!\n"
        "Пожалуйста, выберите удобный язык:\n\n"
        "Welcome to the official <b>Carland</b> bot! 👋\n"
        "Please choose your preferred language:"
    )
    # Start da til tanlash oynasi chiqadi
    await message.answer(
        start_text,
        parse_mode="HTML",
        reply_markup=get_language_inline_keyboard(lang=lang, show_back=False)
    )
    
    # Shuningdek, pastki asosiy boshqaruv menyu tugmalarini darhol chiqarish
    main_menu_prompt = (
        "👇 <b>Quyidagi menyu tugmalaridan ham to'g'ridan-to'g'ri foydalanishingiz mumkin:</b>" if lang == "uz" else (
            "👇 <b>Вы также можете сразу воспользоваться кнопками меню ниже:</b>" if lang == "ru" else
            "👇 <b>You can also use the menu buttons below directly:</b>"
        )
    )
    await message.answer(main_menu_prompt, parse_mode="HTML", reply_markup=get_main_keyboard(lang))


@router.message(Command("lang"))
@router.message(Command("language"))
@router.message(F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Change Language"]))
async def choose_language_handler(message: Message):
    """Tilni o'zgartirish menyusi (Orqaga qaytish tugmasi bilan)"""
    user_id = message.from_user.id if message.from_user else 0
    lang = get_user_lang(user_id)
    text = (
        "🌐 <b>Iltimos, kerakli tilni tanlang:</b>\n"
        "🌐 <b>Пожалуйста, выберите язык:</b>\n"
        "🌐 <b>Please select your language:</b>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_language_inline_keyboard(lang=lang, show_back=True))


@router.message(Command("menu"))
@router.message(F.text.in_([
    "⬅️ Orqaga", "⬅️ Назад", "⬅️ Back",
    "🏠 Asosiy menyu", "🏠 Главное меню", "🏠 Main Menu",
    "Orqaga", "Назад", "Back", "Menyu", "Меню", "Menu"
]))
async def text_back_to_main_handler(message: Message):
    """Matn yoki tugma orqali asosiy menyuga qaytish"""
    user_id = message.from_user.id if message.from_user else 0
    lang = get_user_lang(user_id)
    user_name = message.from_user.full_name if message.from_user else "Hurmatli mijoz"

    if lang == "ru":
        text = (
            f"🏠 <b>Главное меню Carland</b>\n\n"
            f"Здравствуйте, <b>{user_name}</b>! 👋\n"
            "Выберите нужный раздел из меню ниже:"
        )
    elif lang == "en":
        text = (
            f"🏠 <b>Carland Main Menu</b>\n\n"
            f"Hello, <b>{user_name}</b>! 👋\n"
            "Select an option from the menu below:"
        )
    else:
        text = (
            f"🏠 <b>Carland Asosiy Menyusi</b>\n\n"
            f"Assalomu alaykum, <b>{user_name}</b>! 👋\n"
            "Quyidagi menyudan kerakli bo'limni tanlang:"
        )

    await message.answer(text, parse_mode="HTML", reply_markup=get_main_keyboard(lang))


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Help buyrug'i handleri (Ko'p tilli)"""
    user_id = message.from_user.id if message.from_user else 0
    lang = get_user_lang(user_id)

    if lang == "ru":
        help_text = (
            "📖 <b>Руководство по использованию бота:</b>\n\n"
            "• <b>🧮 Подбор масла:</b> Нажмите кнопку в меню или введите модель авто (например: <i>'Cobalt'</i>, <i>'Tracker 2'</i>, <i>'BYD Song'</i>).\n"
            "• <b>📍 Филиалы Carland:</b> Адреса, ориентиры и график работы 15 филиалов (/filiallar).\n"
            "• <b>💬 AI Консультант:</b> Задайте любой интересующий вопрос по автозапчастям и сервису.\n"
            "• <b>🌐 Сменить язык:</b> Команда (/lang).\n"
            "• <b>🧹 Очистить диалог:</b> Сбросить историю переписки с AI (/reset).\n\n"
            "💡 <i>Напоминание: При покупке моторного масла замена БЕСПЛАТНО! За замену масла в коробке передач и редукторе взимается оплата услуги в зависимости от модели авто.</i>"
        )
    elif lang == "en":
        help_text = (
            "📖 <b>Bot User Guide:</b>\n\n"
            "• <b>🧮 Oil Calculator:</b> Tap the button in the menu or type your vehicle model (e.g. <i>'Cobalt'</i>, <i>'Tracker 2'</i>, <i>'BYD Song'</i>).\n"
            "• <b>📍 Carland Branches:</b> Locations, landmarks, and hours of 15 branches (/filiallar).\n"
            "• <b>💬 AI Consultant:</b> Ask any technical or automotive question.\n"
            "• <b>🌐 Change Language:</b> Command (/lang).\n"
            "• <b>🧹 Clear Chat:</b> Reset conversation history (/reset).\n\n"
            "💡 <i>Reminder: Engine oil replacement service is completely FREE! For transmission and differential oil, service fee is charged depending on vehicle model.</i>"
        )
    else:
        help_text = (
            "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
            "• <b>🧮 Moy hisoblash:</b> Menyudagi tugmani bosing yoki to'g'ridan-to'g'ri mashinangiz nomini yozing (masalan: <i>'Cobalt matori'</i>, <i>'Tracker 2 moyi'</i>, <i>'BYD Song Plus'</i>).\n"
            "• <b>📍 Carland filiallari:</b> Toshkent, Samarqand, Buxoro, Qarshi, Chirchiq, Olmaliq va boshqa filiallarimiz mo'ljallari (/filiallar).\n"
            "• <b>💬 AI Maslahatchi:</b> Istalgan savolingizni yozib qoldiring, sun'iy intellekt darhol javob beradi.\n"
            "• <b>🌐 Tilni o'zgartirish:</b> (/lang) buyrug'i orqali.\n"
            "• <b>🧹 Suhbatni tozalash:</b> AI bilan suhbat tarixini yangilash uchun (/reset).\n\n"
            "💡 <i>Eslatma: Mator moyi sotib olinganda almashtirish mutlaqo BEPUL! Karobka va reduktor moyini almashtirishda esa mashina rusumiga qarab xizmat haqi olinadi.</i>"
        )
    await message.answer(help_text, parse_mode="HTML")


def format_branches_text(lang: str = "uz") -> tuple[str, str]:
    """Carland ning 15 ta filiali ro'yxati, ish vaqti va lokatsiyalarini o'zbekcha, ruscha yoki inglizcha formatlash"""
    if lang == "ru":
        part1 = "📍 <b>Филиалы автосервиса Carland (Часть 1):</b>\n\n"
        for i, b in enumerate(CARLAND_BRANCHES[:8], 1):
            name = b.get("name_ru", b["name"])
            address = b.get("address_ru", b["address"])
            orientr = b.get("orientr_ru", b["orientr"])
            part1 += (
                f"<b>{i}. {name}</b>\n"
                f"🕒 Режим работы: <b>{b['working_hours']}</b>\n"
                f"📌 Адрес: {address}\n"
                f"📍 Ориентир: <i>{orientr}</i>\n"
                f"🌐 Локация: <a href=\"{b['location_url']}\">Открыть на карте (Taplink)</a>\n\n"
            )

        part2 = "📍 <b>Филиалы автосервиса Carland (Часть 2):</b>\n\n"
        for i, b in enumerate(CARLAND_BRANCHES[8:], 9):
            name = b.get("name_ru", b["name"])
            address = b.get("address_ru", b["address"])
            orientr = b.get("orientr_ru", b["orientr"])
            part2 += (
                f"<b>{i}. {name}</b>\n"
                f"🕒 Режим работы: <b>{b['working_hours']}</b>\n"
                f"📌 Адрес: {address}\n"
                f"📍 Ориентир: <i>{orientr}</i>\n"
                f"🌐 Локация: <a href=\"{b['location_url']}\">Открыть на карте (Taplink)</a>\n\n"
            )
        part2 += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🕒 <b>Общий режим работы:</b> Каждый день <b>с 09:00 до 23:00</b> без выходных!\n"
            "📞 <b>Единый Call-центр / Связь:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n\n"
            "🛠 <i>При покупке масла в сети Carland — замена масла БЕСПЛАТНО!</i>\n"
            "👇 <b>Кнопки для перехода к карте нужного филиала:</b>"
        )
    elif lang == "en":
        part1 = "📍 <b>Carland Auto Service Branches (Part 1):</b>\n\n"
        for i, b in enumerate(CARLAND_BRANCHES[:8], 1):
            name = b.get("name_en", b["name"])
            address = b.get("address_en", b["address"])
            orientr = b.get("orientr_en", b["orientr"])
            part1 += (
                f"<b>{i}. {name}</b>\n"
                f"🕒 Working hours: <b>{b['working_hours']}</b>\n"
                f"📌 Address: {address}\n"
                f"📍 Landmark: <i>{orientr}</i>\n"
                f"🌐 Location: <a href=\"{b['location_url']}\">Open Map (Taplink)</a>\n\n"
            )

        part2 = "📍 <b>Carland Auto Service Branches (Part 2):</b>\n\n"
        for i, b in enumerate(CARLAND_BRANCHES[8:], 9):
            name = b.get("name_en", b["name"])
            address = b.get("address_en", b["address"])
            orientr = b.get("orientr_en", b["orientr"])
            part2 += (
                f"<b>{i}. {name}</b>\n"
                f"🕒 Working hours: <b>{b['working_hours']}</b>\n"
                f"📌 Address: {address}\n"
                f"📍 Landmark: <i>{orientr}</i>\n"
                f"🌐 Location: <a href=\"{b['location_url']}\">Open Map (Taplink)</a>\n\n"
            )
        part2 += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🕒 <b>General hours:</b> Every day from <b>09:00 to 23:00</b> without days off!\n"
            "📞 <b>Call-Center / Contact:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n\n"
            "🛠 <i>Free oil replacement service when purchasing oil at Carland!</i>\n"
            "👇 <b>Click buttons below to view branch locations:</b>"
        )
    else:
        part1 = "📍 <b>Carland Avtoservis Filiallari (1-qism):</b>\n\n"
        for i, b in enumerate(CARLAND_BRANCHES[:8], 1):
            part1 += (
                f"<b>{i}. {b['name']}</b>\n"
                f"🕒 Ish vaqti: <b>{b['working_hours']}</b>\n"
                f"📌 Manzil: {b['address']}\n"
                f"📍 Mo'ljal: <i>{b['orientr']}</i>\n"
                f"🌐 Lokatsiya: <a href=\"{b['location_url']}\">Xaritada ochish (Taplink)</a>\n\n"
            )

        part2 = "📍 <b>Carland Avtoservis Filiallari (2-qism):</b>\n\n"
        for i, b in enumerate(CARLAND_BRANCHES[8:], 9):
            part2 += (
                f"<b>{i}. {b['name']}</b>\n"
                f"🕒 Ish vaqti: <b>{b['working_hours']}</b>\n"
                f"📌 Manzil: {b['address']}\n"
                f"📍 Mo'ljal: <i>{b['orientr']}</i>\n"
                f"🌐 Lokatsiya: <a href=\"{b['location_url']}\">Xaritada ochish (Taplink)</a>\n\n"
            )
        part2 += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🕒 <b>Umumiy ish vaqti:</b> Har kuni <b>09:00 dan 23:00 gacha</b> dam olish kunlarisiz!\n"
            "📞 <b>Aloqa / Call-center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n\n"
            "🛠 <i>Moy almashtirish va texnik xizmatlar uchun istalgan filialimizga tashrif buyurishingiz mumkin!</i>\n"
            "👇 <b>Quyidagi tugmalar orqali aniq filial xaritasiga o'tishingiz mumkin:</b>"
        )
    return part1, part2


def format_about_text(lang: str = "uz") -> str:
    """Biz haqimizda va aloqa ma'lumotlarini o'zbekcha, ruscha yoki inglizcha formatlash"""
    if lang == "ru":
        return (
            "🏢 <b>Автосервис и Центр Замены Масел Carland</b>\n\n"
            "Мы предоставляем качественное обслуживание более чем в 15 филиалах по всему Узбекистану:\n"
            "✅ Профессиональная замена моторных и трансмиссионных (коробка передач) масел;\n"
            "✅ При покупке моторного масла — <b>ЗАМЕНА АБСОЛЮТНО БЕСПЛАТНО</b>;\n"
            "⚙️ При замене масла в коробке (АКПП/МКПП) и редукторе оплата услуги зависит от модели автомобиля;\n"
            "✅ Оригинальные фильтры (масляные, салонные, воздушные, топливные);\n"
            "✅ Тормозные колодки, свечи зажигания, антифриз и аккумуляторы;\n"
            "✅ Широкий ассортимент шин и балансировка колес;\n"
            "✅ Компьютерная диагностика, автоэлектрик и ремонт ходовой части.\n\n"
            "📍 <b>Главный офис:</b> г. Ташкент, Чиланзарский р-н, ул. Лутфий, 24А\n"
            "📍 <b>Наши филиалы:</b> г. Ташкент и Таш. область, Самарканд, Бухара, Карши (15 филиалов).\n"
            "🕒 <b>Режим работы:</b> Каждый день <b>с 09:00 до 23:00</b> без выходных!\n"
            "📞 <b>Единый Call-центр:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            "✉️ <b>Email:</b> info@carland.uz\n"
            "🌐 <b>Официальный сайт:</b> <a href=\"https://carland.uz/ru\">carland.uz</a>\n"
            "📅 <b>Онлайн-запись на замену масла:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/ru/booking</a>\n\n"
            "<i>По любым вопросам звоните или пишите в этот бот!</i>"
        )
    elif lang == "en":
        return (
            "🏢 <b>Carland Auto Service & Oil Change Center</b>\n\n"
            "We provide premium automotive maintenance across 15+ branches in Uzbekistan:\n"
            "✅ Engine and transmission oil replacement with certified quality oils;\n"
            "✅ <b>FREE OIL REPLACEMENT SERVICE</b> when purchasing engine oil;\n"
            "⚙️ Transmission and differential oil replacement service fee depends on vehicle model;\n"
            "✅ Genuine filters (oil, cabin, air, fuel);\n"
            "✅ Brake pads, spark plugs, coolant (antifreeze), and batteries;\n"
            "✅ Wide selection of tires and wheel balancing;\n"
            "✅ Suspension repair, diagnostics, and auto electrician.\n\n"
            "📍 <b>Head Office:</b> Tashkent, Chilanzar district, Lutfiy street 24A\n"
            "📍 <b>Branches:</b> Tashkent, Samarkand, Bukhara, Karshi, Chirchiq, Olmaliq (15 branches).\n"
            "🕒 <b>Working hours:</b> Every day from <b>09:00 to 23:00</b> without days off!\n"
            "📞 <b>Call-Center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            "✉️ <b>Email:</b> info@carland.uz\n"
            "🌐 <b>Official Website:</b> <a href=\"https://carland.uz\">carland.uz</a>\n"
            "📅 <b>Online Booking:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/ru/booking</a>\n\n"
            "<i>For any inquiries, feel free to call our center or chat with this AI bot!</i>"
        )
    return (
        "🏢 <b>Carland Avtomoylar va Avtoservis Markazi</b>\n\n"
        "Biz O'zbekiston bo'ylab 15 dan ortiq zamonaviy filiallarimizda avtomobillarga sifatli xizmat ko'rsatamiz:\n"
        "✅ Dvigatel va uzatmalar qutisi (karobka) moylarini asl sifatda almashtirish;\n"
        "✅ Dvigatel (mator) moyi sotib olgan mijozlarga <b>ALMASHTIRISH MUTLAQO BEPUL</b>;\n"
        "⚙️ Karobka va reduktor moyini almashtirishda mashina rusumiga qarab xizmat haqi olinadi;\n"
        "✅ Original filtrlar (mator, salon, havo, yonilg'i);\n"
        "✅ Tormoz kolodkalari, svechalar, antifriz va akkumulyatorlar;\n"
        "✅ Balonlar (shinalar) keng assortimenti va balansirirovka;\n"
        "✅ Xodovoy ta'mirlash, diagnostika va avtoelektrik xizmatlari.\n\n"
        "📍 <b>Bosh ofis:</b> Toshkent shahri, Chilonzor tumani, Lutfiy ko'chasi, 24A\n"
        "📍 <b>Filiallarimiz:</b> Toshkent shahri va viloyati, Samarqand, Buxoro, Qarshi (15 ta filial).\n"
        "🕒 <b>Ish vaqti:</b> Har kuni <b>09:00 dan 23:00 gacha</b> dam olish kunlarisiz!\n"
        "📞 <b>Aloqa / Call-center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
        "✉️ <b>Email:</b> info@carland.uz\n"
        "🌐 <b>Rasmiy sayt:</b> <a href=\"https://carland.uz\">carland.uz</a>\n"
        "📅 <b>Onlayn navbatga yozilish:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/ru/booking</a>\n\n"
        "<i>Savollaringiz bo'lsa, istalgan vaqt qo'ng'iroq qilishingiz yoki shu bot orqali ma'lumot olishingiz mumkin!</i>"
    )


@router.message(Command("filiallar"))
@router.message(F.text.in_(["📍 Carland filiallari", "📍 Филиалы Carland", "📍 Carland Branches"]))
async def show_branches_handler(message: Message, lang: str = "uz"):
    """Carland ning 15 ta filiali ro'yxati, ish vaqti va lokatsiyalari"""
    user_id = message.from_user.id if message.from_user else 0
    if not lang or lang == "uz":
        lang = get_user_lang(user_id)

    part1, part2 = format_branches_text(lang)
    await message.answer(part1, parse_mode="HTML", disable_web_page_preview=True)
    await message.answer(part2, parse_mode="HTML", reply_markup=get_branches_links_keyboard(lang), disable_web_page_preview=True)


@router.message(Command("aksiya"))
@router.message(F.text.in_(["🎁 Sentabr Aksiyalari", "🎁 Сентябрьские акции", "🎁 September Promos"]))
async def show_promos_handler(message: Message):
    """Sentabr oyi Call Center maxsus paketlari va aksiyalari"""
    user_id = message.from_user.id if message.from_user else 0
    lang = get_user_lang(user_id)

    if lang == "ru":
        promo_text = (
            "🔥 <b>СПЕЦИАЛЬНЫЕ СЕНТЯБРЬСКИЕ АКЦИИ CARLAND!</b> 🔥\n"
            "<i>Во всех пакетах замена масла и фильтры в ПОДАРОК (БОНУС)!</i>\n\n"
        )
        for key, p in SEPTEMBER_AKSIYALAR.items():
            promo_text += (
                f"<b>{p['title']}</b>\n"
                f"💰 Цена: <b>{p['base_price']}</b>\n"
                f"🚗 Авто: <i>{p['desc']}</i>\n"
                f"🎁 <b>Подарки (Бонусы):</b>\n"
            )
            for b in p['bonuses']:
                promo_text += f"   • {b}\n"
            promo_text += "────────────────────\n\n"
        promo_text += (
            "📍 <i>Акции действуют во всех 15 филиалах!</i>\n"
            "📞 Есть вопросы? Напишите нашему AI консультанту прямо в чат."
        )
    elif lang == "en":
        promo_text = (
            "🔥 <b>CARLAND SPECIAL SEPTEMBER PROMOTIONS!</b> 🔥\n"
            "<i>All packages include FREE oil change and BONUS filters!</i>\n\n"
        )
        for key, p in SEPTEMBER_AKSIYALAR.items():
            promo_text += (
                f"<b>{p['title']}</b>\n"
                f"💰 Price: <b>{p['base_price']}</b>\n"
                f"🚗 Cars: <i>{p['desc']}</i>\n"
                f"🎁 <b>Gifts (Bonuses):</b>\n"
            )
            for b in p['bonuses']:
                promo_text += f"   • {b}\n"
            promo_text += "────────────────────\n\n"
        promo_text += (
            "📍 <i>Promotions are valid at all 15 branches!</i>\n"
            "📞 Any questions? Ask our AI assistant right in the chat."
        )
    else:
        promo_text = (
            "🔥 <b>CARLAND SENTABR OYI MAXSUS AKSIYALARI!</b> 🔥\n"
            "<i>Barcha aksiyalarimizda almashtirish xizmati va filtrlar BONUS!</i>\n\n"
        )
        for key, p in SEPTEMBER_AKSIYALAR.items():
            promo_text += (
                f"<b>{p['title']}</b>\n"
                f"💰 Narxi: <b>{p['base_price']}</b>\n"
                f"🚗 Mos avtolar: <i>{p['desc']}</i>\n"
                f"🎁 <b>Sovg'alar (Bonuslar):</b>\n"
            )
            for b in p['bonuses']:
                promo_text += f"   • {b}\n"
            promo_text += "────────────────────\n\n"
        promo_text += (
            "📍 <i>Aksiyalar barcha 15 ta filialimizda amal qiladi!</i>\n"
            "📞 Savollaringiz bo'lsa, AI maslahatchimizga bemalol yozishingiz mumkin."
        )

    await message.answer(promo_text, parse_mode="HTML")


@router.message(Command("calc"))
@router.message(F.text.in_(["🧮 Moy hisoblash", "🧮 Подбор масла", "🧮 Oil Calculator"]))
async def start_calc_handler(message: Message):
    """Moy hisoblash - markani tanlash"""
    user_id = message.from_user.id if message.from_user else 0
    lang = get_user_lang(user_id)

    if lang == "ru":
        text = (
            "🚘 <b>Калькулятор моторного и трансмиссионного масла:</b>\n\n"
            "Выберите марку вашего автомобиля из списка ниже или просто напишите название в чат "
            "(например: <i>'Cobalt'</i>, <i>'Gentra'</i>, <i>'BYD Song'</i>, <i>'Tracker 2'</i>):"
        )
    elif lang == "en":
        text = (
            "🚘 <b>Oil Calculator:</b>\n\n"
            "Select your car brand from the list below or simply type its name in the chat "
            "(e.g.: <i>'Cobalt'</i>, <i>'Gentra'</i>, <i>'BYD Song'</i>, <i>'Tracker 2'</i>):"
        )
    else:
        text = (
            "🚘 <b>Moy kalkulyatori:</b>\n\n"
            "Quyidagi ro'yxatdan avtomobilingiz markasini tanlang yoki chatga mashinangiz nomini yozing "
            "(masalan: <i>'Cobalt'</i>, <i>'Gentra'</i>, <i>'BYD Song'</i>, <i>'Tracker 2'</i>, <i>'Malibu 2'</i>):"
        )
    await message.answer(text, parse_mode="HTML", reply_markup=get_brands_inline_keyboard(lang))


@router.message(F.text.in_(["⚡ Tezkor narxlar", "⚡ Экспресс цены", "⚡ Quick Prices"]))
async def show_prices_handler(message: Message):
    """Mashhur mahsulotlar va xizmatlar narxlari"""
    user_id = message.from_user.id if message.from_user else 0
    lang = get_user_lang(user_id)

    if lang == "ru":
        text = "⚡ <b>Популярные моторные масла в наличии Carland (за 1 литр):</b>\n\n"
        for name, details in list(POPULAR_OILS.items())[:6]:
            p = f"{details['price_per_liter']:,}".replace(",", " ")
            text += f"• <b>{name}</b>: <code>{p} сум</code>\n  <i>({details['desc']})</i>\n\n"
        text += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 <b>Услуга по замене свечей зажигания на авто GM:</b>\n"
        )
        for auto, data in list(GM_SVECHALAR_PRICING.items())[:6]:
            u = f"{data['usluga']:,}".replace(",", " ")
            text += f"• {auto} ({data['soni']} шт): {u} сум\n"
        text += "\n<i>Узнать точную цену любых запчастей (фильтры, колодки, свечи) можно у AI консультанта!</i>"
    elif lang == "en":
        text = "⚡ <b>Popular engine oils available at Carland (per 1 liter):</b>\n\n"
        for name, details in list(POPULAR_OILS.items())[:6]:
            p = f"{details['price_per_liter']:,}".replace(",", " ")
            text += f"• <b>{name}</b>: <code>{p} UZS</code>\n  <i>({details['desc']})</i>\n\n"
        text += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 <b>Spark plugs replacement labor service (GM cars):</b>\n"
        )
        for auto, data in list(GM_SVECHALAR_PRICING.items())[:6]:
            u = f"{data['usluga']:,}".replace(",", " ")
            text += f"• {auto} ({data['soni']} pcs): {u} UZS\n"
        text += "\n<i>You can ask our AI consultant for any specific part price!</i>"
    else:
        text = "⚡ <b>Carland do'konidagi mashhur moylar narxi (1 litr uchun):</b>\n\n"
        for name, details in list(POPULAR_OILS.items())[:6]:
            p = f"{details['price_per_liter']:,}".replace(",", " ")
            text += f"• <b>{name}</b>: <code>{p} so'm</code>\n  <i>({details['desc']})</i>\n\n"
        text += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 <b>GM avtomobillariga svecha almashtirish xizmati (Usluga):</b>\n"
        )
        for auto, data in list(GM_SVECHALAR_PRICING.items())[:6]:
            u = f"{data['usluga']:,}".replace(",", " ")
            text += f"• {auto} ({data['soni']} dona): {u} so'm\n"
        text += "\n<i>Batafsil istalgan ehtiyot qism (filtr, kolodka, akkumulyator) narxini AI dan so'rashingiz mumkin!</i>"

    await message.answer(text, parse_mode="HTML")


@router.message(Command("ai"))
@router.message(F.text.in_(["💬 AI Maslahatchi", "💬 AI Консультант", "💬 AI Consultant"]))
async def ai_consultant_button_handler(message: Message):
    """AI Maslahatchi bo'limi tugmasi bosilganda tezkor va imloviy xatosiz qo'llanma chiqarish"""
    user_id = message.from_user.id if message.from_user else 0
    lang = get_user_lang(user_id)

    if lang == "ru":
        text = (
            "💬 <b>Добро пожаловать к умному AI консультанту Carland!</b> 🤖\n\n"
            "Я официальный виртуальный консультант сети автосервисов Carland. Чем я могу вам помочь:\n\n"
            "• 🛢 <b>Моторные и трансмиссионные масла:</b> точный объем и вязкость (0W-20, 5W-30, 5W-40, ATF, EV);\n"
            "• 🛑 <b>Запчасти и расходники:</b> цены на колодки (Fourgreen, Hardron), свечи (GM, Autozip, Torch), фильтры, аккумуляторы;\n"
            "• 🛞 <b>Шины:</b> заводские типоразмеры и рекомендации;\n"
            "• 🛠 <b>Услуги автосервиса:</b> замена масла в АКПП/МКПП и редукторах, ремонт ходовой части;\n"
            "• 📍 <b>Филиалы:</b> адреса, ориентиры и график работы всех 15 сервисов.\n\n"
            "💡 <i>Напишите марку вашего автомобиля и интересующий вопрос прямо в чат!</i>\n"
            "<i>Например: «Cobalt матор мойи», «Gentra свеча narxi», «Volkswagen ID 6 reduktor», «Deepal SL03 moy filtri»</i>"
        )
    elif lang == "en":
        text = (
            "💬 <b>Welcome to Carland Smart AI Consultant!</b> 🤖\n\n"
            "I am the official AI assistant of Carland Auto Service network. I can assist you with:\n\n"
            "• 🛢 <b>Engine & Transmission Oils:</b> Exact capacities and viscosity ratings (0W-20, 5W-30, 5W-40, ATF, EV);\n"
            "• 🛑 <b>Spare Parts:</b> Brake pads (Fourgreen, Hardron), spark plugs, filters, batteries;\n"
            "• 🛞 <b>Tires:</b> OEM sizes and recommendations;\n"
            "• 🛠 <b>Service:</b> Transmission fluid flush, differential service, suspension inspection;\n"
            "• 📍 <b>Branches:</b> Locations, working hours, and navigation for 15 branches.\n\n"
            "💡 <i>Type your car model and question directly in the chat!</i>\n"
            "<i>Example: 'Cobalt engine oil', 'Gentra spark plugs', 'Volkswagen ID 6 reductor', 'Deepal SL03 oil filter'</i>"
        )
    else:
        text = (
            "💬 <b>Carland Aqlli AI Maslahatchisiga xush kelibsiz!</b> 🤖\n\n"
            "Men Carland avtoservisining rasmiy aqlli maslahatchisiman. Sizga quyidagi masalalarda yordam bera olaman:\n\n"
            "• 🛢 <b>Mator va karobka moylari:</b> Avtomobilingiz uchun aniq moy hajmi va markasi (0W-20, 5W-30, 5W-40, ATF6, EV);\n"
            "• 🛑 <b>Ehtiyot qismlar va filtrlar:</b> Tormoz kolodkalari, GM svechalar, moy filtrlari va akkumulyator narxlari;\n"
            "• 🛞 <b>Shinalar (balonlar):</b> Zavod o'lchamlari va tavsiyalar;\n"
            "• 🛠 <b>Servis xizmatlari:</b> Mator moyi (bepul almashtirish), karobka va reduktor moyi xizmatlari;\n"
            "• 📍 <b>Filiallar:</b> 15 ta filialimiz manzillari, mo'ljallari va ish vaqti.\n\n"
            "💡 <i>Avtomobilingiz rusumi va savolingizni bemalol chatga yozing!</i>\n"
            "<i>Masalan: «Cobalt mator moyi», «Gentra svecha narxi», «Volkswagen ID 6 reduktor», «Deepal SL03 moy filtri»</i>"
        )

    await message.answer(text, parse_mode="HTML")


@router.message(F.text.in_(["📞 Biz haqimizda & Aloqa", "📞 О нас и Контакты", "📞 About & Contacts"]))
async def about_handler(message: Message, lang: str = "uz"):
    """Biz haqimizda va aloqa ma'lumotlari (O'zbek, Rus va Ingliz tillarida)"""
    user_id = message.from_user.id if message.from_user else 0
    if not lang or lang == "uz":
        lang = get_user_lang(user_id)
    text = format_about_text(lang)
    await message.answer(text, parse_mode="HTML", reply_markup=get_about_keyboard(lang))


@router.message(Command("reset"))
@router.message(F.text.in_(["🧹 Suhbatni tozalash", "🧹 Очистить диалог", "🧹 Clear Chat"]))
async def reset_handler(message: Message):
    """Suhbat tarixini tozalash"""
    user_id = message.from_user.id if message.from_user else 0
    clear_user_chat_history(user_id)
    lang = get_user_lang(user_id)

    if lang == "ru":
        res_text = "🧹 <b>История диалога успешно очищена!</b>\nМожете задать новый вопрос."
    elif lang == "en":
        res_text = "🧹 <b>Chat history has been cleared!</b>\nFeel free to ask a new question."
    else:
        res_text = "🧹 <b>Suhbat tarixi muvaffaqiyatli tozalandi!</b>\nYangi savollaringizni bemalol yozishingiz mumkin."

    await message.answer(res_text, parse_mode="HTML")


# === INLINE CALLBACK QUERY HANDLERS ===

@router.callback_query(F.data.startswith("set_lang:"))
async def set_lang_callback(call: CallbackQuery):
    """Til tanlanganda ishlaydigan callback"""
    lang = call.data.split(":")[1]
    user_id = call.from_user.id
    set_user_lang(user_id, lang)
    user_name = call.from_user.full_name

    if lang == "ru":
        welcome_text = (
            f"Здравствуйте, <b>{user_name}</b>! 👋\n\n"
            "🚗 Добро пожаловать в официальный бот автосервиса и центра замены масел <b>Carland</b>!\n\n"
            "Я помогу вам по 2 основным направлениям:\n"
            "1. 🧮 <b>Подбор и расчет масла для автомобиля:</b>\n"
            "   • Точный объем масла для двигателя, АКПП и редуктора;\n"
            "   • Рекомендуемые допуски и вязкость (0w20, 5w30, 5w40, ATF6, 75w90);\n"
            "   • Интервалы замены фильтров.\n\n"
            "2. 💬 <b>AI Консультант:</b>\n"
            "   • Адреса, ориентиры и график работы 15 филиалов Carland;\n"
            "   • Актуальные цены на масла, фильтры, колодки, свечи и шины;\n"
            "   • Профессиональные консультации по авто.\n\n"
            "🕒 <b>Режим работы:</b> Каждый день <b>с 09:00 до 23:00</b> без выходных!\n"
            "📞 <b>Call-центр:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            "🛠 <i>При покупке моторного масла — замена АБСОЛЮТНО БЕСПЛАТНО! (Замена масла в коробке и редукторе оплачивается в зависимости от модели авто)</i>\n\n"
            "👇 <b>Выберите раздел из меню ниже или напишите ваш вопрос:</b>"
        )
        alert_text = "Язык успешно изменен на Русский! 🇷🇺"
    elif lang == "en":
        welcome_text = (
            f"Hello, <b>{user_name}</b>! 👋\n\n"
            "🚗 Welcome to the official bot of <b>Carland Auto Service & Oil Change Center</b>!\n\n"
            "I can assist you with:\n"
            "1. 🧮 <b>Car Oil Calculator:</b>\n"
            "   • Exact oil capacities for engine, automatic transmission, and differential;\n"
            "   • Recommended oil grades (0w20, 5w30, 5w40, ATF6, 75w90);\n"
            "   • Filter change intervals.\n\n"
            "2. 💬 <b>AI Consultant:</b>\n"
            "   • Addresses, landmarks, and hours of 15 Carland branches;\n"
            "   • Prices for oils, filters, brake pads, spark plugs, and tires;\n"
            "   • Immediate answers to technical questions.\n\n"
            "🕒 <b>Working hours:</b> Every day from <b>09:00 to 23:00</b> without days off!\n"
            "📞 <b>Call-Center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            "🛠 <i>Engine oil replacement service is completely FREE! (For transmission and differential oil, service fee depends on vehicle model)</i>\n\n"
            "👇 <b>Select an option from the menu below or type your question:</b>"
        )
        alert_text = "Language set to English! 🇬🇧"
    else:
        welcome_text = (
            f"Assalomu alaykum, <b>{user_name}</b>! 👋\n\n"
            "🚗 <b>Carland — Avtomobillar Moy Almashtirish va Ehtiyot Qismlar Markazining</b> rasmiy aqlli botiga xush kelibsiz!\n\n"
            "Men sizga 2 ta asosiy yo'nalishda yordam beraman:\n"
            "1. 🧮 <b>Mashinangiz uchun moy hisoblash:</b>\n"
            "   • Mator, Karobka va Reduktorga necha litr moy ketishi;\n"
            "   • Qaysi moy markasi va qovushqoqligi (0w20, 5w30, 5w40, 10w40, ATF6, 75w90) to'g'ri kelishi;\n"
            "   • Filtr almashtirish oraliqlari.\n\n"
            "2. 💬 <b>AI Maslahatchi:</b>\n"
            "   • Carland ning 15 ta filiali manzillari va mo'ljallari;\n"
            "   • Moylar, filtrlar, svechalar, kolodkalar, antifriz va balonlar narxlari;\n"
            "   • Avtomobilingiz bo'yicha istalgan texnik savolingizga javob.\n\n"
            "🕒 <b>Ish vaqti:</b> Har kuni <b>09:00 dan 23:00 gacha</b> dam olish kunlarisiz!\n"
            "📞 <b>Call-center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            "🛠 <i>Dvigatel (mator) moyi sotib olganda almashtirish MUTLAQO BEPUL! (Karobka va reduktor moyini almashtirishda mashina rusumiga qarab xizmat haqi olinadi)</i>\n\n"
            "👇 <b>Quyidagi menyudan kerakli bo'limni tanlang yoki mashinangiz nomini yozing:</b>"
        )
        alert_text = "Til O'zbekchaga o'zgartirildi! 🇺🇿"

    await call.answer(alert_text)
    if call.message and isinstance(call.message, Message):
        await call.message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_keyboard(lang))


@router.callback_query(F.data.startswith("brand:"))
async def brand_selected_callback(call: CallbackQuery):
    """Marka tanlanganda modellarni ko'rsatish"""
    brand = call.data.split(":")[1]
    lang = get_user_lang(call.from_user.id)
    keyboard = get_cars_inline_keyboard(brand, lang)
    
    title = f"🚘 <b>{brand}</b> avtomobillari ro'yxati:\nKerakli modelni tanlang:"
    if lang == "ru":
        title = f"🚘 Список моделей <b>{brand}</b>:\nВыберите нужную модель:"
    elif lang == "en":
        title = f"🚘 Models of <b>{brand}</b>:\nSelect your model:"

    await safe_edit_message(call, title, parse_mode="HTML", reply_markup=keyboard)
    await call.answer()


@router.callback_query(F.data == "back_to_brands")
async def back_to_brands_callback(call: CallbackQuery):
    """Markalar ro'yxatiga qaytish"""
    lang = get_user_lang(call.from_user.id)
    title = "🚘 <b>Moy kalkulyatori:</b>\nAvtomobilingiz markasini tanlang:"
    if lang == "ru":
        title = "🚘 <b>Калькулятор масла:</b>\nВыберите марку автомобиля:"
    elif lang == "en":
        title = "🚘 <b>Oil Calculator:</b>\nSelect your vehicle brand:"

    await safe_edit_message(call, title, parse_mode="HTML", reply_markup=get_brands_inline_keyboard(lang))
    await call.answer()


@router.callback_query(F.data.in_(["back_to_main", "calc_cancel", "main_menu"]))
async def back_to_main_callback(call: CallbackQuery):
    """Asosiy menyuga qaytish callback"""
    user_id = call.from_user.id
    lang = get_user_lang(user_id)
    user_name = call.from_user.full_name or "Hurmatli mijoz"

    if lang == "ru":
        text = (
            f"🏠 <b>Главное меню Carland</b>\n\n"
            f"Здравствуйте, <b>{user_name}</b>! 👋\n"
            "Выберите нужный раздел из меню ниже или напишите ваш вопрос прямо в чат:"
        )
    elif lang == "en":
        text = (
            f"🏠 <b>Carland Main Menu</b>\n\n"
            f"Hello, <b>{user_name}</b>! 👋\n"
            "Select an option from the menu below or type your question in the chat:"
        )
    else:
        text = (
            f"🏠 <b>Carland Asosiy Menyusi</b>\n\n"
            f"Assalomu alaykum, <b>{user_name}</b>! 👋\n"
            "Quyidagi menyudan kerakli bo'limni tanlang yoki savolingizni bemalol yozing:"
        )

    await safe_edit_message(call, text, parse_mode="HTML", reply_markup=None)
    if call.message and isinstance(call.message, Message):
        await call.message.answer(text, parse_mode="HTML", reply_markup=get_main_keyboard(lang))
    await call.answer()


@router.callback_query(F.data.startswith("ask_trans:"))
async def ask_trans_callback(call: CallbackQuery):
    """Uzatmalar qutisi (Mexanika yoki Avtomat) so'rash"""
    car_code = call.data.split(":")[1]
    info = DUAL_TRANSMISSION_CARS.get(car_code)
    car_name = info["name"] if info else car_code.capitalize()
    lang = get_user_lang(call.from_user.id)
    
    if lang == "ru":
        text = (
            f"🚗 Расчет масла для <b>{car_name}</b>:\n\n"
            "<i>💡 В настоящее время преобладают автомобили с АКПП, поэтому Автомат является основным выбором.</i>\n\n"
            "Выберите тип коробки передач:\n"
            "• ⚡️ <b>Автомат (АКПП) — Рекомендуем</b>\n"
            "• 🕹 <b>Механика (МКПП)</b>"
        )
    elif lang == "en":
        text = (
            f"🚗 Oil calculation for <b>{car_name}</b>:\n\n"
            "<i>💡 Automatic transmissions are standard across most modern vehicles.</i>\n\n"
            "Select transmission type:\n"
            "• ⚡️ <b>Automatic (AT) — Recommended</b>\n"
            "• 🕹 <b>Manual (MT)</b>"
        )
    else:
        text = (
            f"🚗 <b>{car_name}</b> uchun moy hisoblash:\n\n"
            "<i>💡 Hozirda ko'pchilik avtomobillar Avtomat bo'lgani sababli, Avtomat asosiy tanlov hisoblanadi.</i>\n\n"
            "Uzatmalar qutisi (karobka) turini tanlang:\n"
            "• ⚡️ <b>Avtomat (AKPP) — Asosiy</b>\n"
            "• 🕹 <b>Mexanika (MKPP)</b>"
        )
    await safe_edit_message(call, text, parse_mode="HTML", reply_markup=get_transmission_keyboard(car_code, lang))
    await call.answer()


@router.callback_query(F.data.startswith("trans:"))
async def trans_selected_callback(call: CallbackQuery):
    """Uzatmalar qutisi tanlanganda aniq hisobot chiqarish"""
    parts = call.data.split(":")
    car_code = parts[1]
    trans_type = parts[2]
    info = DUAL_TRANSMISSION_CARS.get(car_code)
    lang = get_user_lang(call.from_user.id)
    
    if not info:
        await call.answer("Ma'lumot topilmadi!" if lang == "uz" else "Информация не найдена!", show_alert=True)
        return
        
    car_key = info.get(trans_type)
    car_info = CARS_DATABASE.get(car_key)
    
    if not car_info:
        await call.answer("Model ma'lumoti topilmadi!" if lang == "uz" else "Данные модели не найдены!", show_alert=True)
        return

    report = format_car_oil_report(car_info, lang=lang)
    keyboard = get_car_result_keyboard(car_key, lang=lang)
    
    await safe_edit_message(call, report, parse_mode="HTML", reply_markup=keyboard)
    await call.answer()


@router.callback_query(F.data.startswith("car:"))
async def car_selected_callback(call: CallbackQuery):
    """Model tanlanganda hisobotni ko'rsatish"""
    car_key = call.data.split(":")[1]
    car_info = CARS_DATABASE.get(car_key)
    lang = get_user_lang(call.from_user.id)
    
    if not car_info:
        await call.answer("Avtomobil ma'lumotlari topilmadi!" if lang == "uz" else "Информация не найдена!", show_alert=True)
        return

    report = format_car_oil_report(car_info, lang=lang)
    keyboard = get_car_result_keyboard(car_key, lang=lang)
    
    await safe_edit_message(call, report, parse_mode="HTML", reply_markup=keyboard)
    await call.answer()


@router.callback_query(F.data.startswith("branches_lang:"))
async def branches_lang_callback(call: CallbackQuery):
    """Filiallar ro'yxati tilini almashtirish (uz, ru, en)"""
    lang = call.data.split(":")[1]
    user_id = call.from_user.id
    set_user_lang(user_id, lang)
    
    alert_msg = "Til o'zgartirildi" if lang == "uz" else ("Язык переключен" if lang == "ru" else "Language changed")
    await call.answer(alert_msg)
    if call.message and isinstance(call.message, Message):
        part1, part2 = format_branches_text(lang)
        await call.message.answer(part1, parse_mode="HTML", disable_web_page_preview=True)
        await call.message.answer(part2, parse_mode="HTML", reply_markup=get_branches_links_keyboard(lang), disable_web_page_preview=True)


@router.callback_query(F.data.startswith("about_lang:"))
async def about_lang_callback(call: CallbackQuery):
    """Biz haqimizda matni tilini almashtirish (uz, ru, en)"""
    lang = call.data.split(":")[1]
    user_id = call.from_user.id
    set_user_lang(user_id, lang)
    await call.answer()
    if call.message and isinstance(call.message, Message):
        text = format_about_text(lang)
        await safe_edit_message(call, text, parse_mode="HTML", reply_markup=get_about_keyboard(lang))


@router.callback_query(F.data.startswith("ask_ai:"))
async def ask_ai_car_callback(call: CallbackQuery):
    """Tanlangan mashina bo'yicha AI dan maslahat olish"""
    car_key = call.data.split(":")[1]
    car_info = CARS_DATABASE.get(car_key)
    lang = get_user_lang(call.from_user.id)
    
    if car_info:
        if lang == "ru":
            query = f"Какое масло лучше заливать в {car_info['name']} и на что обратить внимание?"
            loading_msg = "AI готовит ответ..."
        elif lang == "en":
            query = f"What oil do you recommend for {car_info['name']} and what precautions are advised?"
            loading_msg = "AI is preparing response..."
        else:
            query = f"{car_info['name']} avtomobiliga qanday moy quyishni tavsiya qilasiz va nimalarga e'tibor berish kerak?"
            loading_msg = "AI javob tayyorlamoqda..."

        await call.answer(loading_msg)
        if call.message and isinstance(call.message, Message) and call.bot:
            async with ChatActionSender.typing(bot=call.bot, chat_id=call.message.chat.id):
                try:
                    ai_reply = await asyncio.wait_for(
                        asyncio.to_thread(get_gemini_response, query, call.from_user.id, lang),
                        timeout=5.0
                    )
                except Exception as e:
                    logger.warning(f"AI timeout yoki xatolik ({e}), fallback ishlatilmoqda")
                    ai_reply = get_fallback_answer(query)
                await safe_send_message(call.message, ai_reply)
    else:
        await call.answer()


@router.callback_query(F.data.startswith("info:"))
async def infographic_callback(call: CallbackQuery):
    """Avtomobil infografikasi tugmasi bosilganda rasmni darhol tayyorlab jo'natish (0.06 soniyada)"""
    parts = call.data.split(":")
    car_key = parts[1]
    info_type = parts[2] if len(parts) > 2 else "umumiy"
    car_info = CARS_DATABASE.get(car_key)
    lang = get_user_lang(call.from_user.id)

    if not car_info:
        await call.answer("Avtomobil ma'lumotlari topilmadi!", show_alert=True)
        return

    wait_msg = "Infografika tayyorlanmoqda..." if lang == "uz" else ("Готовим инфографику..." if lang == "ru" else "Preparing infographic...")
    await call.answer(wait_msg)

    bio = generate_vehicle_infographic(car_info, info_type=info_type, lang=lang)
    photo = BufferedInputFile(bio.getvalue(), filename=f"{car_key}_{info_type}.png")

    titles = {
        "mator": "Dvigatel (Mator) moyi",
        "karobka": "Uzatmalar qutisi (Karobka)",
        "reduktor": "Reduktor moyi",
        "filtrlar": "Filtrlar (Moy, Havo, Salon)",
        "umumiy": "To'liq texnik ma'lumotlar"
    }
    t_name = titles.get(info_type, "Infografika")
    caption = (
        f"📊 <b>{car_info['name']}</b> — {t_name} infografikasi\n\n"
        f"🕒 <b>Ish vaqti:</b> 09:00 - 23:00 | 📞 <b>Call-center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
        f"🌐 <b>Onlayn navbat:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/booking</a>"
    )
    if lang == "ru":
        caption = (
            f"📊 <b>{car_info['name']}</b> — Инфографика ({t_name})\n\n"
            f"🕒 <b>Режим работы:</b> 09:00 - 23:00 | 📞 <b>Call-центр:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            f"🌐 <b>Онлайн-запись:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/booking</a>"
        )
    elif lang == "en":
        caption = (
            f"📊 <b>{car_info['name']}</b> — Infographic ({t_name})\n\n"
            f"🕒 <b>Hours:</b> 09:00 - 23:00 | 📞 <b>Call-Center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            f"🌐 <b>Booking:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/booking</a>"
        )

    nav_keyboard = get_infographic_nav_keyboard(car_key, current_type=info_type, lang=lang)
    if call.message and isinstance(call.message, Message):
        await call.message.answer_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=nav_keyboard)


# === MATNLI XABARLAR (TEXT MESSAGES & AI) ===

@router.message(F.text)
async def text_message_handler(message: Message):
    """Foydalanuvchi matnli xabar yozganda yashin tezligida (0.001 soniyada) javob berish"""
    if not message.text or not message.bot or not message.chat:
        return
        
    t_start = time.time()
    text = message.text.strip()
    text_lower = text.lower()
    user_id = message.from_user.id if message.from_user else 0
    current_lang = get_user_lang(user_id)
    
    # Tilni matn orqali aniqlash
    is_russian_text = any(c in text_lower for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    is_english_text = any(w in text_lower.split() for w in ["what", "how", "when", "where", "price", "brake", "plug", "oil", "hello", "hi", "change", "hours", "open"])
    
    lang = "ru" if is_russian_text else ("en" if is_english_text else current_lang)
    logger.info(f"📩 Yangi xabar [User: {user_id}, Lang: {lang}]: '{text}'")

    # 0. Ish vaqti, aloqa yoki call-center so'ralganda (0.001 soniyada)
    is_asking_hours_contact = any(k in text_lower for k in [
        "ish vaqti", "telefon", "nomer", "aloqa", "kontakt", "call center", "call-center", "raqam", "bog'lanish", "boglanish",
        "время работы", "график работы", "режим работы", "до скольки", "когда работаете", "связь", "связаться",
        "working hours", "hours", "open", "phone", "contact", "call"
    ])
    if is_asking_hours_contact:
        if lang == "ru":
            text_contact = (
                "🏢 <b>Автосервис и Центр Обслуживания Carland:</b>\n\n"
                "🕒 <b>Режим работы:</b> Каждый день <b>с 09:00 до 23:00</b> без выходных!\n"
                "📞 <b>Единый Call-центр:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                "📍 <b>Наши филиалы:</b> Ташкент, Самарканд, Бухара, Карши, Чирчик, Алмалык (15 филиалов).\n\n"
                "<i>Чтобы посмотреть адреса и карты всех филиалов, нажмите /filiallar!</i>"
            )
        elif lang == "en":
            text_contact = (
                "🏢 <b>Carland Auto Service & Service Center:</b>\n\n"
                "🕒 <b>Working hours:</b> Every day from <b>09:00 to 23:00</b> without days off!\n"
                "📞 <b>Call-Center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                "📍 <b>Branches:</b> Tashkent, Samarkand, Bukhara, Karshi, Chirchiq, Olmaliq (15 branches).\n\n"
                "<i>To view branch locations and maps, use command /filiallar!</i>"
            )
        else:
            text_contact = (
                "🏢 <b>Carland Ish Vaqti va Aloqa Markazi:</b>\n\n"
                "🕒 <b>Ish vaqti:</b> Har kuni <b>09:00 dan 23:00 gacha</b> dam olish kunlarisiz!\n"
                "📞 <b>Aloqa / Call-center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                "📍 <b>Filiallar:</b> Toshkent, Samarqand, Buxoro, Qarshi, Chirchiq, Olmaliq (15 ta filial).\n\n"
                "<i>Filiallarning to'liq ro'yxati va lokatsiyalarini ko'rish uchun /filiallar buyrug'ini bosing!</i>"
            )
        await safe_send_message(message, text_contact)
        logger.info(f"⚡️ Javob yuborildi (Ish vaqti/Aloqa) [{time.time() - t_start:.3f}s] [User: {user_id}]")
        return

    # 1. Filiallar yoki lokatsiyalar so'ralganda darhol (0.001 soniyada)
    is_asking_branches = any(k in text_lower for k in [
        "filial", "filiallar", "manzil", "lokatsiya", "qayerda", "orientr",
        "филиал", "филиалы", "адрес", "адреса", "где вы", "локация", "ориентир", "где находитесь",
        "branch", "branches", "location", "locations", "address"
    ])
    if is_asking_branches:
        await show_branches_handler(message, lang=lang)
        logger.info(f"⚡️ Javob yuborildi (Filiallar) [{time.time() - t_start:.3f}s] [User: {user_id}]")
        return

    # 2. Aksiyalar so'ralganda darhol (0.001 soniyada)
    if any(k in text_lower for k in ["aksiya", "aksiyalar", "paket", "paketlar", "skidka", "акция", "акции", "скидка", "promo"]):
        await show_promos_handler(message)
        logger.info(f"⚡️ Javob yuborildi (Aksiyalar) [{time.time() - t_start:.3f}s] [User: {user_id}]")
        return

    # 2.5. Aqlli Qisqa Savollarni Anglash (Smart Intent Resolver - 0.001 soniyada)
    # Masalan: "Kobalt R15", "Gentra kalotka", "Tracker svecha", "Kobalt 5w30", "Kobalt karobka"
    smart_reply = resolve_smart_intent(text, lang=lang)
    if smart_reply:
        await safe_send_message(message, smart_reply)
        logger.info(f"⚡️ Javob yuborildi (Smart Intent) [{time.time() - t_start:.3f}s] [User: {user_id}]")
        return

    # 2.8. Infografika rasmi so'ralganda (0.06 soniyada rasm generatsiya qilib jo'natish)
    is_asking_photo = any(k in text_lower for k in [
        "infografika", "rasm", "rasmi", "rasmini", "rasmlari", "foto", "fotosi",
        "картинка", "инфографика", "фото", "рисунок", "image", "picture", "infographic"
    ])
    matched_car = find_car_by_query(text)
    if is_asking_photo and matched_car and isinstance(matched_car, dict):
        if any(w in text_lower for w in ["karobka", "akpp", "mkpp", "коробка", "кпп", "gearbox", "transmission"]):
            info_type = "karobka"
        elif any(w in text_lower for w in ["reduktor", "редуктор", "reductor", "differential"]):
            info_type = "reduktor"
        elif any(w in text_lower for w in ["filtr", "filtri", "filtrlar", "salon", "vazdush", "havo", "фильтр", "салон", "воздушный", "filter"]):
            info_type = "filtrlar"
        elif any(w in text_lower for w in ["mator", "motor", "dvigatel", "матор", "мотор", "двигатель", "engine"]):
            info_type = "mator"
        else:
            info_type = "umumiy"

        car_key = next((k for k, v in CARS_DATABASE.items() if v["name"] == matched_car["name"]), "cobalt")
        bio = generate_vehicle_infographic(matched_car, info_type=info_type, lang=lang)
        photo = BufferedInputFile(bio.getvalue(), filename=f"{car_key}_{info_type}.png")

        t_names = {
            "mator": "Dvigatel (Mator) moyi",
            "karobka": "Uzatmalar qutisi (Karobka)",
            "reduktor": "Reduktor moyi",
            "filtrlar": "Filtrlar (Moy, Havo, Salon)",
            "umumiy": "To'liq texnik ma'lumotlar"
        }
        t_name = t_names.get(info_type, "Infografika")
        caption = (
            f"📊 <b>{matched_car['name']}</b> — {t_name} infografikasi\n\n"
            f"🕒 <b>Ish vaqti:</b> 09:00 - 23:00 | 📞 <b>Call-center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            f"🌐 <b>Onlayn navbat:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/booking</a>"
        )
        if lang == "ru":
            caption = (
                f"📊 <b>{matched_car['name']}</b> — Инфографика ({t_name})\n\n"
                f"🕒 <b>Режим работы:</b> 09:00 - 23:00 | 📞 <b>Call-центр:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"🌐 <b>Онлайн-запись:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/booking</a>"
            )
        elif lang == "en":
            caption = (
                f"📊 <b>{matched_car['name']}</b> — Infographic ({t_name})\n\n"
                f"🕒 <b>Hours:</b> 09:00 - 23:00 | 📞 <b>Call-Center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"🌐 <b>Booking:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/booking</a>"
            )
        nav_keyboard = get_infographic_nav_keyboard(car_key, current_type=info_type, lang=lang)
        await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=nav_keyboard)
        logger.info(f"⚡️ Infografika yuborildi: {matched_car['name']} ({info_type}) [{time.time() - t_start:.3f}s]")
        return

    # 2.9. To'g'ridan-to'g'ri berilgan savollarni chuqur o'rganib javob berish
    # Foydalanuvchi botga savol, maslahat yoki taqqoslash bergan bo'lsa
    # (masalan: "Cobalt gazda yursa qaysi moy yaxshi?", "Tracker 2 ga 5w30 quysa boladimi?", "VW ID 4 reduktor moyi narxi qancha?", "Gentra 180 ming yurgan"):
    # Savolni chuqur o'rganib, avtomobil parametrlari bilan boyitilgan holda professional javob beriladi.
    if is_direct_question(text):
        async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
            car_key = next((k for k, v in CARS_DATABASE.items() if v["name"] == matched_car["name"]), "") if (matched_car and isinstance(matched_car, dict)) else ""
            reply_markup = get_car_result_keyboard(car_key, lang=lang) if car_key else None

            try:
                ans = await asyncio.wait_for(
                    asyncio.to_thread(answer_automotive_question, text, user_id, lang, matched_car if isinstance(matched_car, dict) else None),
                    timeout=5.5
                )
            except Exception as e:
                logger.warning(f"Direct question javobida xatolik/timeout ({e}), smart lokal motor ishlatilmoqda")
                ans = smart_automotive_answer(text, car=matched_car if isinstance(matched_car, dict) else None, lang=lang)

            await safe_send_message(message, ans, reply_markup=reply_markup)
            logger.info(f"⚡️ To'g'ridan-to'g'ri savolga javob berildi [{time.time() - t_start:.3f}s] [User: {user_id}]")
            return

    # 3. Avtomobil nomi aniqlanganda va boshqa ehtiyot qism so'ralmaganda (moy kalkulyatori 0.001 soniyada)
    is_asking_other_parts = any(k in text_lower for k in [
        "kolodka", "kalotka", "tormoz", "nakladka", "колодки", "колодка", "brake",
        "svecha", "svechalar", "свечи", "свеча", "spark", "plug",
        "shina", "balon", "antifriz", "akkumulyator", "pampers", "babina"
    ])
    
    if matched_car and isinstance(matched_car, dict) and not is_asking_other_parts:
        report = format_car_oil_report(matched_car, lang=lang)
        car_key = next((k for k, v in CARS_DATABASE.items() if v["name"] == matched_car["name"]), "")
        reply_markup = get_car_result_keyboard(car_key, lang=lang) if car_key else None
        
        header = f"✅ <b>{matched_car['name']} uchun moy hisoboti:</b>"
        if lang == "ru":
            header = f"✅ <b>Отчет по маслам для {matched_car['name']}:</b>"
        elif lang == "en":
            header = f"✅ <b>Oil report for {matched_car['name']}:</b>"

        await safe_send_message(
            message,
            f"{header}\n\n{report}",
            reply_markup=reply_markup
        )
        logger.info(f"⚡️ Javob yuborildi (Moy hisoboti: {matched_car['name']}) [{time.time() - t_start:.3f}s] [User: {user_id}]")
        return

    # 4. Yashin tezligidagi to'g'ridan-to'g'ri javoblar (0.001 soniyada - salomlashish, karobka/reduktor xizmat haqi, mator bepulligi, sayt/booking, ofis, xizmatlar, akkumulyator, shina, antifriz, vakansiya, b2b)
    direct_fast_ans = get_fast_direct_answer(text, lang=lang)
    if direct_fast_ans:
        await safe_send_message(message, direct_fast_ans)
        logger.info(f"⚡️ Javob yuborildi (Fast direct answer) [{time.time() - t_start:.3f}s] [User: {user_id}]")
        return

    # 5. Tormoz kolodkalari, svechalar yoki moy narxlari (0.001 soniyada lokal ma'lumotlar bazasidan)
    if any(k in text_lower for k in ["kolodka", "kalotka", "tormoz", "nakladka", "колодки", "brake", "svecha", "svechalar", "свечи", "spark", "moy narxi", "цена масла"]):
        fast_reply = get_fallback_answer(text)
        if "Savolingiz qabul qilindi" not in fast_reply and "принят" not in fast_reply:
            await safe_send_message(message, fast_reply)
            logger.info(f"⚡️ Javob yuborildi (Ehtiyot qismlar) [{time.time() - t_start:.3f}s] [User: {user_id}]")
            return

    # 6. Boshqa murakkab / umumiy savollar uchun Asinxron AI (7.0 soniya timeout bilan)
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            ai_reply = await asyncio.wait_for(
                asyncio.to_thread(get_gemini_response, text, user_id, lang),
                timeout=7.0
            )
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"AI timeout yoki xatolik ({e}), tezkor zaxira javob ishlatilmoqda")
            ai_reply = get_fallback_answer(text)
            
        await safe_send_message(message, ai_reply)
        logger.info(f"🤖 Javob yuborildi (Gemini AI) [{time.time() - t_start:.3f}s] [User: {user_id}]")
