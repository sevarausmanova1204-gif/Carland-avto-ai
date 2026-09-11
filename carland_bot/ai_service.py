# pyright: reportPrivateImportUsage=false
"""
Carland AI Xizmati
Google Gemini AI (va OpenAI zaxira) orqali mijozlarga Carland avtoservis
bilimlar bazasi asosida professional javob beruvchi intellektual modul.
"""

import logging
import re
from typing import Dict, Any, Optional
import google.generativeai as genai
from config import GEMINI_API_KEY
from carland_knowledge import CARLAND_BRANCHES, SPECIAL_TERMINOLOGY, POPULAR_OILS
from car_data import find_car_by_query
from smart_intent import is_direct_question

logger = logging.getLogger(__name__)

# System Prompt tayyorlash (Yengil va yuqori tezlikdagi model uchun)
def build_carland_system_prompt() -> str:
    return """Sen - "Carland" avtoservis va avtomoylar markazining rasmiy aqlli AI maslahatchisisan.
Mijozlarga avtomobil moylari, filtrlar, svechalar, akkumulyatorlar, tormoz kolodkalari, shinalar va servis xizmatlari bo'yicha qisqa, professional, aniq va xushmuomala maslahat ber.

MUHIM QOIDALAR:
1. Ish vaqti: Har kuni 09:00 dan 23:00 gacha dam olish kunlarisiz! (Каждый день с 09:00 до 23:00 без выходных! / Everyday 09:00 - 23:00 without days off).
2. Yagona Call-Center: +998 55 516 16 16.
3. Rasmiy veb-sayt: https://carland.uz (Onlayn navbatga yozilish: https://carland.uz/ru/booking, mobil ilova: Carland).
4. Bosh ofis: Toshkent shahri, Chilonzor tumani, Lutfiy ko'chasi 24A (Yandex xarita orqali oson topiladi).
5. Filiallar: Toshkent shahri va viloyatlarda 15 ta zamonaviy filial mavjud (/filiallar buyrug'i orqali xaritalar va manzillar ko'rsatiladi).
6. 🛢 Dvigatel (mator) moyi xarid qilinganda, uni almashtirish xizmati MUTLAQO BEPUL! (Faqat mator moyi uchun bepul).
7. ⚙️ Karobka (AKPP/MKPP) va reduktor moyini almashtirishda mashina rusumiga qarab xizmat haqi olinadi (Avtomat karobka apparatda yuvish aksiyasi — 720 000 so'm).
8. ⚡️ Texnik talablar va yangi modellar:
   - Cobalt va yangi Gentra matoriga 3.5 litr moy, avtomat karobkasiga (AKPP) 7 litr ATF6 quyiladi.
   - GAC Aion S+: To'liq elektr (EV). Reduktor moyi: 1 litr EV moy + 200 000 so'm xizmat haqi (usluga).
   - BYD Yuan Up (Gibrid): Matoriga 4 litr 0w20, reduktoriga 2.2 litr EV moy.
   - BYD to'liq elektr (EV modellar): Reduktor moyi 1 litr EV moy.
   - Volkswagen ID.4: To'liq elektr (EV), dvigatel moyi yo'q. Reduktoriga 1 litr D1 / EV moylar quyiladi.
   - Volkswagen ID.6: To'liq elektr (EV), dvigatel moyi yo'q. Reduktoriga oldiga 600 gr EV/D2, orqaga 1 litr EV/D2 quyiladi.
   - Chery Aiqar EQ7: To'liq elektr (EV), dvigatel moyi yo'q. Reduktoriga 2 litr EV moy quyiladi.
   - Deepal SL03 (Gibrid): Matoriga 4 litr 0w20, moy filtri OP 621, reduktoriga 1.5 litr EV/D2 quyiladi.
9. 10 ta asosiy xizmat: Mator moyi (bepul almashtirish), Karobka va reduktor moyi, Tormoz kolodkalari, Xodovoy ta'miri, Shinomontaj va balansirovka, Avtoelektrik va kompyuter diagnostikasi, Akkumulyatorlar (STARTER CMF), Svechalar almashtirish, Yonilg'i baki va benzanasos tozalash.
10. Tillar: Foydalanuvchi qaysi tilda murojaat qilsa (O'zbekcha, Ruscha yoki Inglizcha), aynan o'sha tilda ravon, xushmuomala, emoji bilan chiroyli formatlangan qisqa javob qaytar.
11. Imlo va til madaniyati: Har doim toza, to'g'ri, adabiy o'zbek tilida yoz ('avtomobilingiz', 'mashinangiz', 'xizmatingizdamiz'). Hech qachon 'avtomansingiz' yoki shunga o'xshash buzilgan, xato so'zlarni ishlatma!
12. To'g'ridan-to'g'ri berilgan savollarni chuqur o'rganib, to'liq va professional javob berish:
    - Gaz (metan/propan) o'rnatilgan dvigatellarga: gaz yuqori haroratda (~2000°C) yonadi. Shu sababli termik barqarorligi yuqori to'liq sintetik 5W-30 (yoki 150 000 km dan oshgan bo'lsa 5W-40) tavsiya etiladi (Shell Helix Ultra, Motul, Liqui Moly, Korelux X500, Aveno). Almashtirish oralig'i: 6 000 - 7 000 km.
    - Probegi 100k - 150k km dan oshgan yoki moy kamaytirayotgan dvigatellarga: 0W-20 o'rniga qalinroq 5W-30 yoki 5W-40 sintetik moy quyish, klapan salniklari (kolpachok) va sapunkni tekshirish tavsiya etiladi.
    - Tracker 2 / Onix 1.0T va 1.2T dvigatellariga: qat'iy ravishda 0W-20 Dexos 1 Gen 3 quyilishi SHART! Sababi: gaz taqsimlash remeni (GRM) moy vannasi ichida ishlaydi (wet belt). Qalin 5W-30 yoki 5W-40 quyilsa, remen yemirilib mator ishdan chiqadi va LSPI effekti yuzaga keladi.
    - Avtomat karobka moyini apparatda yuvish: oddiy to'kishda faqat 50% eski moy chiqadi, maxsus apparatda yuvish esa gidrotransformator va butun tizimdagi kirlarni 98-100% yuvib yangilaydi (Carland aksiyasi: 720 000 so'm).
    - Elektromobil va Gibrid reduktorlari (ID.4, ID.6, BYD Yuan Up, BYD EV, Chery EQ7, Deepal SL03): har 40 000 - 50 000 km da maxsus EV / D2 / D1 moyi quyiladi, xizmat haqi pullik.
    - Dvigatel (mator) moyi xarid qilinganda uni almashtirish xizmati MUTLAQO BEPUL! Karobka va reduktor moyini almashtirishda mashina rusumiga qarab xizmat haqi olinadi."""


# User sessiyalari xotirasi
user_chat_sessions: Dict[int, Any] = {}
user_history: Dict[int, list] = {}

FAST_GEN_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.8,
    "max_output_tokens": 400,
}

# Tezkor javob kesh (0.001 soniya ichida javob berish uchun)
RESPONSE_CACHE: Dict[str, str] = {}

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)  # type: ignore
    except Exception as e:
        logger.error(f"Gemini sozlashda xatolik: {e}")

# Pre-compiled system prompt va singleton model
_system_prompt_cache = None
_cached_gemini_model = None

def get_or_create_model():
    """Gemini modelini faqat bir marta yaratish (har bir so'rovda qayta yaratilmaydi)"""
    global _cached_gemini_model, _system_prompt_cache
    if _cached_gemini_model is None and GEMINI_API_KEY:
        try:
            if _system_prompt_cache is None:
                _system_prompt_cache = build_carland_system_prompt()
            _cached_gemini_model = genai.GenerativeModel(  # type: ignore
                model_name="gemini-3.5-flash-lite",
                system_instruction=_system_prompt_cache,
                generation_config=FAST_GEN_CONFIG  # type: ignore
            )
            logger.info("Gemini 3.5 Flash-Lite modeli muvaffaqiyatli ishga tushirildi (Singleton)")
        except Exception as e:
            logger.error(f"Gemini model yaratishda xatolik: {e}")
            try:
                _cached_gemini_model = genai.GenerativeModel(  # type: ignore
                    model_name="gemini-flash-lite-latest",
                    system_instruction=_system_prompt_cache,
                    generation_config=FAST_GEN_CONFIG  # type: ignore
                )
            except Exception as e2:
                logger.error(f"Zaxira model yaratishda xatolik: {e2}")
    return _cached_gemini_model


def get_fast_direct_answer(query: str, lang: str = "uz") -> Any:
    """Eng ko'p beriladigan umumiy qisqa savollarga 0.001 soniyada yashin tezligida javob berish"""
    # Agar foydalanuvchi to'g'ridan-to'g'ri tahliliy savol bergan bo'lsa,
    # uni quruq shablon bilan to'xtatmaymiz (AI va avtomobil tahlili ishlashi uchun)
    if is_direct_question(query):
        return None

    q = query.lower().strip()
    is_ru = (lang == "ru") or any(c in q for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    is_en = (lang == "en") or any(w in q.split() for w in ["what", "how", "when", "where", "price", "brake", "pad", "pads", "plug", "plugs", "oil", "spark", "hours", "contact", "phone", "hello", "hi", "open", "branch", "branches"])

    # 1. Salomlashish va AI Maslahatchi murojaatlari
    if any(q.startswith(w) or q == w for w in ["salom", "assalom", "privet", "привет", "здравствуйте", "hello", "hi", "qale", "qalesiz"]) or any(k in q for k in ["ai maslahatchi", "ai консультант", "ai consultant", "maslahatchi"]):
        if is_ru:
            return (
                "Здравствуйте! 👋\n\n"
                "🚗 Добро пожаловать в официальный бот <b>Carland</b>!\n"
                "Чем я могу вам помочь?\n"
                "• 🧮 Напишите марку авто (например: <i>'Cobalt'</i>, <i>'Tracker'</i>) для расчета масла;\n"
                "• 🛑 Спросите о запчастях (например: <i>'колодки'</i>, <i>'свечи'</i>, <i>'аккумулятор'</i>);\n"
                "• 📍 Посмотреть адреса всех филиалов: /filiallar;\n"
                "• 📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>."
            )
        elif is_en:
            return (
                "Hello! 👋\n\n"
                "🚗 Welcome to the official <b>Carland</b> bot!\n"
                "How can I assist you?\n"
                "• 🧮 Type your car model (e.g. <i>'Cobalt'</i>, <i>'Tracker'</i>) for oil calculator;\n"
                "• 🛑 Inquire about parts (e.g. <i>'brake pads'</i>, <i>'spark plugs'</i>, <i>'battery'</i>);\n"
                "• 📍 View branch locations: /filiallar;\n"
                "• 📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>."
            )
        return (
            "Assalomu alaykum! 👋\n\n"
            "🚗 <b>Carland</b> rasmiy aqlli botiga xush kelibsiz!\n"
            "Sizga qanday yordam bera olaman?\n"
            "• 🧮 Mashinangiz nomini yozing (masalan: <i>'Cobalt'</i>, <i>'Gentra'</i>) — moy hisobotini olasiz;\n"
            "• 🛑 Ehtiyot qism so'rang (masalan: <i>'kalotka'</i>, <i>'svecha'</i>, <i>'akkumulyator'</i>);\n"
            "• 📍 Filiallar ro'yxatini ko'rish uchun: /filiallar;\n"
            "• 📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>."
        )

    # 2. Karobka va Reduktor xizmat haqi haqida qisqa so'rov
    is_fee_query = (
        any(w in q for w in ["hizmat haqi", "xizmat haqi", "xizmat haqqi", "usluga", "стоимость услуги", "цена замены", "labor fee", "service fee"])
        and any(w in q for w in ["karobka", "reduktor", "atf", "коробк", "редуктор", "transmission"])
    )
    if is_fee_query:
        if is_ru:
            return (
                "⚙️ <b>Замена масла в КПП и редукторе:</b>\n\n"
                "• В сервисах Carland <b>замена масла в коробке передач (АКПП/МКПП) и редукторе платная (оплата услуги зависит от модели автомобиля)</b>.\n"
                "• 🛢 При покупке <b>моторного масла</b> замена производится <b>АБСОЛЮТНО БЕСПЛАТНО</b>!\n"
                "• 💡 <i>Акция: Полная аппаратная промывка и замена масла в АКПП — 720 000 сум!</i>\n\n"
                "📞 Уточнить стоимость для вашей модели: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> или /filiallar."
            )
        elif is_en:
            return (
                "⚙️ <b>Transmission & Differential Oil Replacement:</b>\n\n"
                "• At Carland centers, <b>labor fee for transmission and differential oil replacement depends on the vehicle model</b>.\n"
                "• 🛢 When purchasing <b>engine oil</b>, replacement is completely <b>FREE</b>!\n\n"
                "📞 Contact our call-center for specific pricing: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> or /filiallar."
            )
        return (
            "⚙️ <b>Karobka va Reduktor moyini almashtirish xizmati:</b>\n\n"
            "• Carland servislarida <b>karobka va reduktor moylarini almashtirishda mashina rusumiga qarab xizmat haqi olinadi</b>.\n"
            "• 🛢 <b>Dvigatel (mator) moyi</b> xarid qilinganda esa almashtirish xizmati <b>MUTLAQO BEPUL</b> amalga oshiriladi!\n"
            "• 💡 <i>Aksiya: Avtomat karobka moyini maxsus apparatda to'liq yuvish va almashtirish — 720 000 so'm!</i>\n\n"
            "📞 O'z avtomobilingiz rusumi bo'yicha aniq xizmat narxini bilish uchun: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> yoki /filiallar orqali bog'lanishingiz mumkin."
        )

    # 3. Sayt, onlayn navbat (booking), ilova
    if any(w in q for w in ["sayt", "site", "veb", "online", "onlayn", "booking", "navbat", "yozilish", "ilova", "app", "prilojeniye"]):
        if is_ru:
            return (
                "🌐 <b>Официальный сайт и онлайн-сервисы Carland:</b>\n\n"
                "• 💻 <b>Сайт:</b> <a href=\"https://carland.uz/ru\">carland.uz</a>\n"
                "• 📅 <b>Онлайн-запись на замену масла:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/ru/booking</a>\n"
                "• 📱 <b>Мобильное приложение Carland:</b> в App Store и Google Play;\n"
                "• ✉️ <b>Email:</b> info@carland.uz\n"
                "• 📞 <b>Call-центр:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
            )
        elif is_en:
            return (
                "🌐 <b>Carland Official Website & Online Services:</b>\n\n"
                "• 💻 <b>Website:</b> <a href=\"https://carland.uz\">carland.uz</a>\n"
                "• 📅 <b>Online Booking:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/ru/booking</a>\n"
                "• 📱 <b>Mobile App:</b> Available on App Store and Google Play;\n"
                "• ✉️ <b>Email:</b> info@carland.uz\n"
                "• 📞 <b>Call-Center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
            )
        return (
            "🌐 <b>Carland Rasmiy Sayti va Onlayn Xizmatlar:</b>\n\n"
            "• 💻 <b>Rasmiy veb-sayt:</b> <a href=\"https://carland.uz\">carland.uz</a>\n"
            "• 📅 <b>Moy almashtirishga onlayn yozilish:</b> <a href=\"https://carland.uz/ru/booking\">carland.uz/ru/booking</a>\n"
            "• 📱 <b>Mobil ilova:</b> App Store va Google Play'da <i>'Carland'</i> nomli ilova mavjud;\n"
            "• ✉️ <b>Email:</b> info@carland.uz\n"
            "• 📞 <b>Call-center:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
        )

    # 4. Bosh ofis
    if any(w in q for w in ["bosh ofis", "glavniy ofis", "chilonzor", "lutfiy"]):
        return (
            "🏢 <b>Carland Bosh Ofisi:</b>\n\n"
            "📍 Toshkent shahri, Chilonzor tumani, Lutfiy ko'chasi, 24A\n"
            "🌐 Xaritada ochish: <a href=\"https://yandex.uz/maps/-/CHg9bHjn\">Yandex Xarita</a>\n"
            "📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            "🕒 Ish vaqti: Har kuni 09:00 dan 23:00 gacha"
        )

    # 5. Xizmatlar
    if any(w in q for w in ["xizmatlar", "servislar", "qanday xizmat", "услуги", "сервисы", "services"]):
        if is_ru:
            return (
                "🛠 <b>Услуги автосервиса Carland:</b>\n\n"
                "1. 🛢 <b>Замена моторного масла</b> — при покупке масла замена <b>БЕСПЛАТНО</b>;\n"
                "2. ⚙️ <b>Замена масла в АКПП/МКПП</b> — оплата услуги по модели авто (акция на аппаратную промывку — 720 000 сум);\n"
                "3. 🔄 <b>Замена масла в редукторе</b> (электромобили и гибриды);\n"
                "4. 🛑 <b>Замена тормозных колодок</b> (Fourgreen, Hardron, GM, Japanparts);\n"
                "5. 🚗 <b>Диагностика и ремонт ходовой части</b> (подвеска, амортизаторы);\n"
                "6. 🛞 <b>Шиномонтаж и балансировка колес</b>;\n"
                "7. ⚡️ <b>Автоэлектрик и компьютерная диагностика</b>;\n"
                "8. 🔋 <b>Замена аккумулятора</b> (STARTER CMF и др.);\n"
                "9. 🔧 <b>Замена свечей зажигания</b>;\n"
                "10. ⛽️ <b>Ремонт бензобака и топливной системы</b>.\n\n"
                "🕒 Режим работы: 09:00 - 23:00 без выходных\n"
                "📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                "📅 Онлайн-запись: <a href=\"https://carland.uz/ru/booking\">carland.uz/ru/booking</a>"
            )
        return (
            "🛠 <b>Carland Avtoservis Xizmatlari:</b>\n\n"
            "1. 🛢 <b>Dvigatel moyini almashtirish</b> — Mator moyi xarid qilinganda almashtirish <b>MUTLAQO BEPUL</b>!\n"
            "2. ⚙️ <b>Karobka (AKPP/MKPP) moyi</b> — Mashina rusumiga qarab xizmat haqi olinadi (apparatda yuvish bilan 720 000 so'm aksiya);\n"
            "3. 🔄 <b>Reduktor moyi</b> — Elektromobillar va gibridlar (EV) uchun;\n"
            "4. 🛑 <b>Tormoz tizimi va kolodkalar almashtirish</b>;\n"
            "5. 🚗 <b>Xodovoy qismini diagnostika va ta'mirlash</b>;\n"
            "6. 🛞 <b>Shinomontaj va balansirovka</b>;\n"
            "7. ⚡️ <b>Avtoelektrik va kompyuter diagnostikasi</b>;\n"
            "8. 🔋 <b>Akkumulyator almashtirish</b> (STARTER CMF);\n"
            "9. 🔧 <b>Svechalar almashtirish</b>;\n"
            "10. ⛽️ <b>Benzobak va yonilg'i tizimini ta'mirlash</b>.\n\n"
            "🕒 Ish vaqti: 09:00 - 23:00 dam olish kunlarisiz\n"
            "📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            "📅 Onlayn navbat: <a href=\"https://carland.uz/ru/booking\">carland.uz/ru/booking</a>"
        )

    # 6. Akkumulyator
    if any(w in q for w in ["akkum", "akkumulyator", "аккумулятор", "battery"]):
        return (
            "🔋 <b>Carland da sifatli akkumulyatorlar:</b>\n\n"
            "• STARTER CMF 60AR 60Ah — 855 000 so'm\n"
            "• Delkor, Bars va boshqa barcha avtomobillar uchun akkumulyatorlar mavjud.\n"
            "• Filiallarimizda o'rnatib berish va diagnostika xizmati bor!\n"
            "📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
        )

    # 7. Shina / Balon / Shinomontaj
    if any(w in q for w in ["shina", "balon", "shinomontaj", "balansirovka", "шины", "шиномонтаж"]):
        return (
            "🛞 <b>Carland Shinomontaj va Balonlar:</b>\n\n"
            "• Yozgi va qishki avtomobil shinalari keng assortimenti;\n"
            "• Professional shinomontaj va g'ildiraklarni aniq balansirovka qilish;\n"
            "• Shina bosimini tekshirish va to'g'rilash.\n"
            "📍 O'zingizga yaqin filialni bilish uchun /filiallar buyrug'ini bosing!"
        )

    # 8. Antifriz
    if any(w in q for w in ["antifriz", "tosol", "антифриз", "тосол", "coolant"]):
        return (
            "❄️ <b>Carland do'konlarida Antifriz:</b>\n\n"
            "• Felix, Sintec, Nord va sifatli G11, G12, G12+ antifrizlar mavjud;\n"
            "• Sovutish tizimini to'liq tekshirish va almashtirish xizmati ko'rsatiladi.\n"
            "📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
        )

    # 9. Vakansiyalar
    if any(w in q for w in ["vakansiya", "ishga", "ish bormi", "rabota", "вакансии"]):
        return (
            "💼 <b>Carland Vakansiyalari va Ishga Qabul:</b>\n\n"
            "Carland jamoasiga qo'shilish va ochiq vakansiyalar bilan tanishish uchun rasmiy telegram botimizga kiring:\n"
            "👉 <a href=\"https://t.me/carland_job_bot\">@carland_job_bot</a>"
        )

    # 10. B2B / Yuridik shaxslar
    if any(w in q for w in ["b2b", "yuridik", "korporativ", "perechisleniye"]):
        return (
            "🤝 <b>Yuridik shaxslar (B2B) uchun hamkorlik:</b>\n\n"
            "Carland korporativ mijozlar uchun shartnoma asosida to'lov (perechisleniye), schyot-faktura va maxsus xizmatlarni taqdim etadi.\n"
            "🌐 Batafsil: <a href=\"https://carland.uz/ru/pages/b2b_sale\">carland.uz B2B</a>\n"
            "📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
        )

    return None


def smart_automotive_answer(query: str, car: Optional[Dict[str, Any]] = None, lang: str = "uz") -> str:
    """
    To'g'ridan-to'g'ri berilgan har qanday avtomobil savolini (gaz, probeg, moy turi, karobka, reduktor, filtr, narx)
    chuqur o'rganib, zudlik bilan eng yuqori darajada professional javob beruvchi intellektual motor.
    """
    q = query.lower().strip()
    is_ru = (lang == "ru") or any(c in q for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    is_en = (lang == "en") or any(w in q.split() for w in ["what", "how", "when", "where", "price", "brake", "oil", "gas", "mileage"])
    
    # Mashina aniqlanmagan bo'lsa, matndan qidirib ko'ramiz
    if not car:
        car = find_car_by_query(query)
        
    car_name = car["name"] if car else "avtomobilingiz"
    engine_oil = car.get("engine_oil", "3.5 - 4.0 litr") if car else "3.5 - 4.0 litr"
    engine_type = car.get("engine_oil_type", "5W-30") if car else "5W-30"
    gearbox_oil = car.get("gearbox_oil", "-") if car else "-"
    reductor_oil = car.get("reductor_oil", "-") if car else "-"

    # 1. GAZ / METAN / PROPAN BO'YICHA SAVOLLAR
    if any(w in q for w in ["gaz", "metan", "propan", "газ", "метан", "пропан", "gas", "cng", "lpg"]):
        if is_ru:
            return (
                f"🚗 <b>Рекомендация по маслу для {car_name} на газу (метан/пропан):</b>\n\n"
                f"• При работе на газе температура горения в цилиндрах выше (~2000°C), чем на бензине. Поэтому маслу требуется высокая термическая стабильность и стойкость к окислению.\n\n"
                f"1. 🛢 <b>Вязкость и допуски:</b>\n"
                f"• Оптимальный выбор: <b>5W-30</b> (полная синтетика) — отлично защищает двигатель от перегрева летом и легко запускается зимой.\n"
                f"• Если пробег превышает 150 000 км или есть легкий расход масла — переходите на <b>5W-40</b>.\n"
                f"• Рекомендуемые бренды: <b>Shell Helix Ultra</b>, <b>Motul 8100</b>, <b>Liqui Moly</b>, <b>Korelux X500</b>, <b>Aveno DX2</b>.\n\n"
                f"2. 🔄 <b>Интервал замены:</b>\n"
                f"• На газу масло вырабатывает присадки быстрее — рекомендуется менять каждые <b>6 000 - 7 000 км</b>.\n"
                f"• Объем заливки в двигатель {car_name}: <b>{engine_oil}</b>.\n\n"
                f"🛠 <b>ВАЖНЕЙШЕЕ ПРАВИЛО CARLAND:</b> При покупке моторного масла в наших филиалах, замена масла — <b>АБСОЛЮТНО БЕСПЛАТНО!</b>\n\n"
                f"🕒 Режим работы: <b>09:00 - 23:00</b> ежедневно | 📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"📍 Филиалы: /filiallar"
            )
        elif is_en:
            return (
                f"🚗 <b>Engine Oil Guide for {car_name} on Gas (CNG / LPG):</b>\n\n"
                f"• Natural gas and propane burn at higher combustion temperatures (~2000°C), requiring high thermal resistance and low volatility engine oils.\n\n"
                f"1. 🛢 <b>Viscosity & Recommendation:</b>\n"
                f"• Best choice: <b>5W-30</b> Full Synthetic (or <b>5W-40</b> if mileage exceeds 150,000 km).\n"
                f"• Recommended brands: <b>Shell Helix Ultra</b>, <b>Motul</b>, <b>Liqui Moly</b>, <b>Korelux X500</b>, <b>Aveno</b>.\n"
                f"• Engine oil capacity for {car_name}: <b>{engine_oil}</b>.\n\n"
                f"2. 🔄 <b>Service Interval:</b>\n"
                f"• Every <b>6,000 - 7,000 km</b> for optimal engine longevity.\n\n"
                f"🛠 <b>CARLAND POLICY:</b> Engine oil replacement service is <b>100% FREE</b> with oil purchase!\n\n"
                f"🕒 Hours: 09:00 - 23:00 everyday | 📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
            )
        return (
            f"🚗 <b>{car_name} uchun gazda (metan / propan) yurish bo'yicha moy tavsiyasi:</b>\n\n"
            f"• Gaz benzinga nisbatan ancha yuqori haroratda (~2000°C) yonadi. Shu sababli dvigatel moyining termik chidamliligi va tozalovchi qo'shimchalari yuqori bo'lishi talab etiladi.\n\n"
            f"1. 🛢 <b>Tavsiya etiladigan moy qovushqoqligi:</b>\n"
            f"• <b>5W-30</b> to'liq sintetik moyi — gazda yuradigan avtomobillar uchun eng optimal va ishonchli tanlov!\n"
            f"• Agar mashinangiz probegi 150 000 km dan oshgan bo'lsa yoki ozroq moy yeyish (jor) kuzatilsa, <b>5W-40</b> quyish tavsiya qilinadi.\n"
            f"• Tavsiya qilinadigan brendlar: <b>Shell Helix Ultra</b>, <b>Motul 8100</b>, <b>Liqui Moly</b>, <b>Korelux X500</b>, <b>Aveno DX2</b>.\n\n"
            f"2. 🔄 <b>Almashtirish oralig'i:</b>\n"
            f"• Gazda ishlaydigan dvigatellarda moyni har <b>6 000 - 7 000 km</b> da almashtirish mator resursini maksimal darajada saqlaydi.\n"
            f"• {car_name} dvigateliga quyiladigan moy hajmi: <b>{engine_oil}</b>.\n\n"
            f"🛠 <b>CARLAND DA MUHIM QOIDA:</b> Servislarimizdan mator moyi xarid qilsangiz, uni almashtirib berish <b>MUTLAQO BEPUL!</b>\n\n"
            f"🕒 Ish vaqti: <b>09:00 dan 23:00 gacha</b> dam olish kunlarisiz\n"
            f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            f"📍 Filiallar: /filiallar"
        )

    # 2. TURBO ENGINES (Tracker 2, Onix, Malibu 2 Turbo) / 0W-20 vs 5W-30
    is_turbo_query = (
        any(w in q for w in ["tracker", "onix", "malibu", "turbo", "0w20", "dexos"])
        or (car and any(k in car.get("name", "").lower() for k in ["tracker", "onix"]))
    )
    if is_turbo_query and any(w in q for w in ["quysa boladimi", "quyish mumkinmi", "5w30", "5w40", "0w20", "nega", "sababi", "можно ли", "почему", "стоит ли", "farqi"]):
        if is_ru:
            return (
                f"⚠️ <b>Важное техническое правило для двигателей Tracker 2 / Onix (1.0T / 1.2T):</b>\n\n"
                f"• Для этих турбомоторов <b>СТРОГО требуется масло 0W-20 с допуском Dexos 1 Gen 3</b>!\n\n"
                f"❌ <b>Почему категорически нельзя заливать 5W-30 или 5W-40?</b>\n"
                f"1. <b>Ремень ГРМ в масляной ванне (Wet Belt):</b> В двигателях Tracker 2 и Onix ремень ГРМ омывается моторным маслом. Неправильное или густое масло разъедает корд ремня, резина осыпается, забивает масляный насос и приводит к обрыву ремня и поломке мотора!\n"
                f"2. <b>Защита от LSPI:</b> Турбированный мотор прямого впрыска подвержен риску преждевременного зажигания на низких оборотах. Допуск Dexos 1 Gen 3 полностью защищает поршни от разрушения.\n\n"
                f"• Объем заливки масла: <b>4.0 литра</b>.\n"
                f"🛠 При покупке моторного масла в Carland замена <b>БЕСПЛАТНАЯ!</b>\n\n"
                f"📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
            )
        return (
            f"⚠️ <b>Tracker 2 va Onix (1.0T / 1.2T) dvigatellari uchun qat'iy texnik talab:</b>\n\n"
            f"• Ushbu turbomotorlarga <b>faqat va faqat 0W-20 Dexos 1 Gen 3</b> to'liq sintetik moyi quyilishi SHART!\n\n"
            f"❌ <b>Nega 5W-30 yoki 5W-40 quyish qat'iyan man etiladi?</b>\n"
            f"1. <b>Moy vannasidagi GRM remeni (Wet Belt):</b> Tracker 2 va Onix motorlarida gaz taqsimlash remeni motor moyi ichida suzib aylanadi. Qalin yoki nostandart moy remen kauchukini parchalab yuboradi, rezina qirindilari moy nasosining setkasini to'sib, matorni qisqa vaqtda klapanlar urilishiga (klapan sinishiga) olib keladi!\n"
            f"2. <b>LSPI himoyasi:</b> Turbinalik to'g'ridan-to'g'ri purkash tizimida past aylanishlarda muddatidan oldin portlash sodir bo'lmasligi uchun aynan Dexos 1 Gen 3 maxsus qo'shimchalari kerak.\n\n"
            f"• Mator moyi hajmi: <b>4.0 litr</b>.\n"
            f"🛠 Carland servislarida mator moyi xarid qilsangiz, almashtirish xizmati <b>MUTLAQO BEPUL!</b>\n\n"
            f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
        )

    # 3. KATTA PROBEG VA MOY YEYISH (MASLOJORA / KAMAYISHI / TUTASH)
    if any(w in q for w in ["probeg", "yurgan", "100 ming", "150 ming", "200 ming", "yeyapti", "kamayapti", "maslojora", "жор", "жрет", "ест масло", "пробег", "дым"]):
        if is_ru:
            return (
                f"🔧 <b>Рекомендации при высоком пробеге и расходе масла ({car_name}):</b>\n\n"
                f"1. 🛢 <b>Переход на более плотную вязкость:</b>\n"
                f"• Если на масле 0W-20 или 5W-30 начался угар, рекомендуется перейти на термостабильное синтетическое <b>5W-40</b> (Shell Helix Ultra, Valvoline MaxLife, Motul).\n\n"
                f"2. 🔍 <b>Основные причины расхода масла (жор):</b>\n"
                f"• Затвердевание маслосъемных колпачков клапанов;\n"
                f"• Залегание поршневых колец из-за нагара;\n"
                f"• Неисправность клапана вентиляции картерных газов (сапун);\n"
                f"• Использование некачественного или поддельного масла.\n\n"
                f"🛠 В сервисах Carland мастера проведут диагностику и подберут надежное масло!\n"
                f"🛢 Замена моторного масла при покупке — <b>БЕСПЛАТНО!</b>\n\n"
                f"📞 Запись на диагностику: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
            )
        return (
            f"🔧 <b>Katta probeg va moy kamayishi (yeyishi) bo'yicha mutaxassis maslahati:</b>\n\n"
            f"1. 🛢 <b>Moy qovushqoqligini to'g'ri tanlash ({car_name}):</b>\n"
            f"• Agar avtomobilingiz probegi 100 000 - 150 000 km dan oshgan bo'lsa va moy sathi kamayayotgan bo'lsa, 0W-20 o'rniga yuqori haroratda plyonkasi mustahkam <b>5W-30</b> yoki <b>5W-40</b> to'liq sintetik moyiga o'tish tavsiya etiladi (Shell Helix Ultra, Valvoline MaxLife, Motul 8100, Korelux X500).\n\n"
            f"2. 🔍 <b>Moy yeyishning asosiy sabablari:</b>\n"
            f"• Klapan salniklari (kolpachok) vaqt o'tib qotishi va moy o'tkazishi;\n"
            f"• Porshen xalqalari (koltsa) koks bosib qisilib qolishi;\n"
            f"• Karter gazlari ventilyatsiyasi klapani (sapunk) ifloslanishi;\n"
            f"• Sifatsiz moy quyilishi oqibatida qizib bug'lanib ketishi.\n\n"
            f"🛠 Carland servislarida tajribali ustalar dvigatelni to'liq tekshirib berishadi!\n"
            f"🛢 Mator moyi xarid qilinsa, almashtirish <b>MUTLAQO BEPUL!</b>\n\n"
            f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
        )

    # 4. AVTOMAT KAROBKA APPARATDA YUVISH VA ALMASHTIRISH
    if any(w in q for w in ["apparat", "yuvish", "yuvdir", "to'liq", "промывка", "аппарат", "аппаратная", "flush"]):
        if is_ru:
            return (
                f"⚙️ <b>Преимущества полной аппаратной замены масла в АКПП:</b>\n\n"
                f"• <b>Обычный частичный слив:</b> сливается лишь 40-50% объема из поддона, а старое горелое масло и осадок остаются в гидротрансформаторе и каналах;\n"
                f"• 🚀 <b>Аппаратная замена под давлением:</b> подключается к контуру охлаждения КПП и вытесняет <b>98-100% старого масла</b>, промывая всю гидросистему и заполняя ее чистым свежим ATF!\n\n"
                f"🎁 <b>СПЕЦИАЛЬНАЯ АКЦИЯ CARLAND:</b>\n"
                f"Полная аппаратная промывка и замена масла в АКПП — <b>720 000 сум!</b>\n\n"
                f"📞 Запись на аппаратную замену: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"🌐 Онлайн-запись: <a href=\"https://carland.uz/ru/booking\">carland.uz/booking</a>"
            )
        return (
            f"⚙️ <b>Avtomat uzatmalar qutisi (AKPP) moyini apparatda yuvishning afzalliklari:</b>\n\n"
            f"• <b>Oddiy qo'lda to'kib quyish:</b> karobka karteridan eski moyning faqat 40-50% qismi chiqadi, gidrotransformator va gidroblok kanallarida kirlangan eski moy qolib ketadi;\n"
            f"• 🚀 <b>Maxsus avtomatlashtirilgan apparatda yuvish:</b> tizimga maxsus shlanglar orqali ulanib, bosim ostida butun karobkadagi eski moy, cho'kmalar va metall qirindilarini <b>98-100% to'liq yuvib chiqaradi</b> hamda yangi ATF moyini bir maromda to'ldiradi!\n\n"
            f"🎁 <b>CARLAND MAXSUS AKSIYASI:</b>\n"
            f"Avtomat karobka moyini apparatda to'liq yuvish va almashtirish xizmati — <b>720 000 so'm!</b>\n\n"
            f"📞 Call-center orqali navbatga yozilish: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            f"🌐 Onlayn yozilish: <a href=\"https://carland.uz/ru/booking\">carland.uz/booking</a>"
        )

    # 5. ELEKTROMOBIL VA GIBRID REDUKTORI (ID.4, ID.6, BYD, EQ7, DEEPAL)
    is_ev_reductor = any(w in q for w in ["reduktor", "редуктор", "differensial", "дифференциал", "ev moy", "d1", "d2"]) or (car and car.get("category") in ["Volkswagen", "BYD", "Chery", "Zeekr", "GAC", "Changan (Deepal)"])
    if is_ev_reductor and any(w in q for w in ["reduktor", "moy", "almashtir", "narx", "qancha", "qachon", "редуктор", "масло"]):
        if is_ru:
            return (
                f"⚡️ <b>Замена масла в редукторе электромобилей и гибридов ({car_name}):</b>\n\n"
                f"• В электромобилях нет моторного масла, но редуктор испытывает колоссальные нагрузки от электромотора с первых секунд разгона.\n"
                f"• 🔄 <b>Регламент замены:</b> каждые <b>40 000 - 50 000 км</b>;\n"
                f"• 🛢 <b>Применяемое масло:</b> Специальное низковязкое диэлектрическое масло класса <b>EV / D1 / D2</b>;\n"
                f"• ⚙️ <b>Параметры для моделей:</b>\n"
                f"  - <i>Volkswagen ID.4:</i> 1 литр (D1 / EV);\n"
                f"  - <i>Volkswagen ID.6:</i> Передний — 600 гр, Задний — 1 литр (EV/D2);\n"
                f"  - <i>BYD Full EV:</i> 1 литр EV;\n"
                f"  - <i>BYD Yuan Up (Гибрид):</i> Двигатель 4L 0W-20, Редуктор 2.2L EV;\n"
                f"  - <i>Chery Aiqar EQ7:</i> 2 литра EV;\n"
                f"  - <i>Deepal SL03 (Гибрид):</i> Двигатель 4L 0W-20 (фильтр OP 621), Редуктор 1.5L EV/D2;\n"
                f"  - <i>GAC Aion S+:</i> 1 литр EV + 200 000 сум услуга.\n\n"
                f"🛠 <b>ВАЖНО:</b> Замена масла в редукторе — платная услуга сервиса (зависит от модели).\n\n"
                f"📞 Запись и консультация: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )
        return (
            f"⚡️ <b>Elektromobillar va Gibridlar reduktor moyi xizmati ({car_name}):</b>\n\n"
            f"• Elektromobillarda dvigatel (mator) bo'lmaydi, ammo elektr motorining katta aylanish momentini g'ildiraklarga uzatib beruvchi reduktor (differensial) mavjud.\n"
            f"• 🔄 <b>Almashtirish oralig'i:</b> har <b>40 000 - 50 000 km</b> da almashtirish shart;\n"
            f"• 🛢 <b>Moy turi:</b> Maxsus past qovushqoqlikli dielektrik <b>EV / D1 / D2</b> moylari quyiladi;\n"
            f"• ⚙️ <b>Modellar bo'yicha hajmlar:</b>\n"
            f"  - <i>Volkswagen ID.4:</i> 1 litr (D1 / EV);\n"
            f"  - <i>Volkswagen ID.6:</i> Oldiga 600 gr, Orqaga 1 litr (EV/D2);\n"
            f"  - <i>BYD To'liq Elektr (EV):</i> 1 litr EV moy;\n"
            f"  - <i>BYD Yuan Up (Gibrid):</i> Matoriga 4L 0W-20, Reduktoriga 2.2L EV;\n"
            f"  - <i>Chery Aiqar EQ7:</i> 2 litr EV moy;\n"
            f"  - <i>Deepal SL03 (Gibrid):</i> Matoriga 4L 0W-20 (moy filtri OP 621), Reduktoriga 1.5L EV/D2;\n"
            f"  - <i>GAC Aion S+:</i> 1 litr EV + 200 000 so'm xizmat haqi.\n\n"
            f"🛠 <b>MUHIM:</b> Reduktor moyini almashtirish mashina rusumiga qarab pullik xizmat hisoblanadi.\n\n"
            f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
        )

    # 6. MATOR MOYINI ALMASHTIRISH ORALIG'I (NECHA KM DA ALMASHTIRISH KERAK)
    if any(w in q for w in ["necha km", "oralig", "qachon almashtir", "qancha yursa", "сколько км", "интервал", "когда менять", "interval"]):
        if is_ru:
            return (
                f"🕒 <b>Регламент и интервалы замены моторного масла ({car_name}):</b>\n\n"
                f"• <b>Полная синтетика (0W-20, 5W-30):</b> каждые <b>7 000 - 8 000 км</b>;\n"
                f"• <b>В городском цикле (пробки, прогревы) или на газу:</b> каждые <b>6 000 - 7 000 км</b>;\n"
                f"• <b>Полусинтетика (10W-40):</b> каждые <b>5 000 - 6 000 км</b>;\n"
                f"• <b>Фильтры:</b> Масляный фильтр меняется обязательно с каждой заменой масла. Воздушный и салонный фильтры — каждые 10 000 - 15 000 км.\n\n"
                f"🛠 При покупке моторного масла в Carland замена <b>БЕСПЛАТНАЯ!</b>\n\n"
                f"📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>"
            )
        return (
            f"🕒 <b>Dvigatel (mator) moyini almashtirish oraliqlari ({car_name}):</b>\n\n"
            f"• <b>To'liq sintetik moylar (0W-20, 5W-30):</b> har <b>7 000 - 8 000 km</b> da;\n"
            f"• <b>Shahar tirbandliklarida yoki gazda (metan/propan):</b> har <b>6 000 - 7 000 km</b> da;\n"
            f"• <b>Yarim sintetik moylar (10W-40):</b> har <b>5 000 - 6 000 km</b> da;\n"
            f"• <b>Filtrlar:</b> Moy filtri har bir moy almashtirishda yangilanadi. Havo va salon filtrlari esa har 10 000 - 15 000 km da almashtirilishi kerak.\n\n"
            f"🛠 <b>CARLAND QOIDASI:</b> Dvigatel moyi xarid qilinganda almashtirish xizmati <b>MUTLAQO BEPUL!</b>\n\n"
            f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
        )

    # 7. MATOR MOYI ALMASHTIRISH BEPULMI?
    if any(w in q for w in ["bepulmi", "tekinmi", "pullikmi", "бесплатно ли", "платная ли", "is it free"]):
        if is_ru:
            return (
                "🛢 <b>Да, замена моторного масла в Carland АБСОЛЮТНО БЕСПЛАТНАЯ!</b>\n\n"
                "• При покупке моторного масла любого бренда (Shell, Motul, Castrol, Liqui Moly, Valvoline, Korelux, Aveno) наши мастера заменят его <b>совершенно бесплатно</b>!\n"
                "• ⚠️ <i>Обратите внимание: Бесплатная замена действует только на моторное масло. Замена масла в КПП и редукторе является платной услугой (зависит от модели авто).</i>\n\n"
                "📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )
        return (
            "🛢 <b>Ha, albatta! Carland'da mator moyini almashtirish MUTLAQO BEPUL!</b>\n\n"
            "• Carland filiallaridan istalgan brenddagi (Shell, Motul, Castrol, Liqui Moly, Valvoline, Korelux, Aveno) dvigatel moyi xarid qilinsa, ustalarimiz uni <b>100% BEPUL</b> almashtirib berishadi!\n"
            "• ⚠️ <i>Eslatma: Bepul almashtirish faqat dvigatel moyiga tegishli. Karobka va reduktor moylarini almashtirishda mashina modeliga qarab xizmat haqi olinadi.</i>\n\n"
            "📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
        )

    # 8. UMUMIY AVTO SAVOL / ZAXIRA
    if car:
        if is_ru:
            return (
                f"🚗 <b>Техническая информация по {car_name}:</b>\n\n"
                f"• 🛢 <b>Двигатель:</b> {engine_oil} ({engine_type})\n"
                f"• ⚙️ <b>Коробка передач:</b> {gearbox_oil}\n"
                + (f"• ⚡️ <b>Редуктор:</b> {reductor_oil}\n" if reductor_oil != "-" else "") +
                f"• 🔄 <b>Регламент фильтров:</b> {car.get('filter_interval', '20 000 km')}\n\n"
                f"🛠 При покупке моторного масла в сети Carland замена <b>БЕСПЛАТНАЯ!</b>\n"
                f"🕒 Режим работы: 09:00 - 23:00 ежедневно\n"
                f"📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"📍 Филиалы: /filiallar"
            )
        return (
            f"🚗 <b>{car_name} bo'yicha texnik ma'lumot va maslahat:</b>\n\n"
            f"• 🛢 <b>Dvigatel (mator):</b> {engine_oil} ({engine_type})\n"
            f"• ⚙️ <b>Karobka:</b> {gearbox_oil}\n"
            + (f"• ⚡️ <b>Reduktor:</b> {reductor_oil}\n" if reductor_oil != "-" else "") +
            f"• 🔄 <b>Filtrlar oralig'i:</b> {car.get('filter_interval', '20 000 km')}\n\n"
            f"🛠 <b>CARLAND QOIDASI:</b> Mator moyi xarid qilinganda almashtirish <b>MUTLAQO BEPUL!</b>\n"
            f"🕒 Ish vaqti: Har kuni 09:00 dan 23:00 gacha\n"
            f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            f"📍 Filiallar: /filiallar"
        )

    return get_fallback_answer(query)


def answer_automotive_question(
    text: str,
    user_id: int,
    lang: str = "uz",
    car_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    To'g'ridan-to'g'ri berilgan savollarni avtomobil bazasi ma'lumotlari bilan boyitib (context injection),
    Gemini AI orqali chuqur o'rganib to'liq javob qaytaradi.
    Agar Gemini sekinlashsa yoki xatolik yuz bersa, smart_automotive_answer darhol javob beradi.
    """
    cache_key = f"auto_q:{lang}:{text.lower().strip()}"
    if cache_key in RESPONSE_CACHE:
        return RESPONSE_CACHE[cache_key]

    if not car_context:
        car_context = find_car_by_query(text)

    # 1. Gemini AI orqali boyitilgan prompt bilan javob olish
    if GEMINI_API_KEY:
        try:
            model = get_or_create_model()
            if model:
                car_info_text = ""
                if car_context:
                    car_info_text = (
                        f"AVTOMOBILNING BAZADAGI TEXNIK PARAMETRLARI:\n"
                        f"- Rusumi: {car_context.get('name')}\n"
                        f"- Mator moyi hajmi va turi: {car_context.get('engine_oil')} ({car_context.get('engine_oil_type')})\n"
                        f"- Karobka moyi: {car_context.get('gearbox_oil')}\n"
                        f"- Reduktor moyi: {car_context.get('reductor_oil')}\n"
                        f"- Filtr intervali: {car_context.get('filter_interval')}\n"
                        f"- Qo'shimcha: {car_context.get('notes', '-')}\n\n"
                    )

                prompt = (
                    f"{car_info_text}"
                    f"FOYDALANUVCHINING ANIQ SAVOLI:\n{text}\n\n"
                    f"VAZIFA: Ushbu savolni chuqur o'rganib, Carland avtoservisining yetuk mutaxassisi sifatida to'liq, "
                    f"tushunarli va professional javob ber. Agar gaz (metan/propan), katta probeg, moy turi, turbo "
                    f"yoki apparatda yuvish so'ralgan bo'lsa, sabablarini aniq tushuntir. "
                    f"Carland qoidalarini eslat: mator moyi xarid qilinganda almashtirish MUTLAQO BEPUL! "
                    f"Ish vaqti: 09:00 - 23:00 dam olishsiz, Call-center: +998 55 516 16 16. "
                    f"Javobni foydalanuvchi tilida ({lang}) chiroyli formatda va emoji bilan taqdim et."
                )

                res = model.generate_content(prompt)
                if res and res.text:
                    ans = res.text.strip()
                    if len(RESPONSE_CACHE) < 500:
                        RESPONSE_CACHE[cache_key] = ans
                    return ans
        except Exception as e:
            logger.warning(f"answer_automotive_question da Gemini xatoligi ({e}), smart lokal javob ishlatilmoqda")

    # 2. Zaxira intellektual motor (0.001 soniya)
    smart_ans = smart_automotive_answer(text, car=car_context, lang=lang)
    RESPONSE_CACHE[cache_key] = smart_ans
    return smart_ans


def get_gemini_response(prompt: str, user_id: int, lang: str = "uz") -> str:
    """Gemini AI dan tezkor javob olish (Singleton model va Fast answer bilan)"""
    # 1. Keshni tekshirish (0.0001s)
    cache_key = f"{lang}:{prompt.lower().strip()}"
    if cache_key in RESPONSE_CACHE:
        return RESPONSE_CACHE[cache_key]

    # 2. Yashin tezligidagi to'g'ridan-to'g'ri javob tekshiruvi (faqat oddiy qisqa FAQ uchun)
    if not is_direct_question(prompt):
        fast = get_fast_direct_answer(prompt, lang=lang)
        if fast:
            RESPONSE_CACHE[cache_key] = fast
            return fast

    if not GEMINI_API_KEY:
        if is_direct_question(prompt):
            return smart_automotive_answer(prompt, lang=lang)
        return get_fallback_answer(prompt)

    # 3. Singleton modeldan foydalanish
    try:
        model = get_or_create_model()
        if model:
            if user_id not in user_history:
                user_history[user_id] = []
            chat = model.start_chat(history=user_history[user_id][-4:])
            lang_prompt = prompt
            if lang == "ru" and not any(c in prompt for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
                lang_prompt += " (Ответь на русском языке)"
            elif lang == "en" and not any(w in prompt.lower() for w in ["hello", "hi", "what", "how", "oil"]):
                lang_prompt += " (Answer in English)"

            response = chat.send_message(lang_prompt)
            if response and response.text:
                res_text = response.text.strip()
                user_history[user_id].append({"role": "user", "parts": [prompt]})
                user_history[user_id].append({"role": "model", "parts": [res_text]})
                if len(RESPONSE_CACHE) < 500:
                    RESPONSE_CACHE[cache_key] = res_text
                return res_text
    except Exception as e:
        logger.warning(f"Gemini chaqirishda xatolik ({e}), fallback ishlatiladi")

    # 4. Zaxira javob
    if is_direct_question(prompt):
        fallback_res = smart_automotive_answer(prompt, lang=lang)
    else:
        fallback_res = get_fallback_answer(prompt)
    RESPONSE_CACHE[cache_key] = fallback_res
    return fallback_res


def clear_user_chat_history(user_id: int):
    """Foydalanuvchi suhbat tarixini tozalash"""
    if user_id in user_history:
        user_history[user_id] = []
    if user_id in user_chat_sessions:
        del user_chat_sessions[user_id]


def get_fallback_answer(query: str) -> str:
    """
    Lokal bilimlar bazasidan qidirib TO'G'RIDAN-TO'G'RI javob beruvchi funksiya.
    """
    q = query.lower().strip()
    is_ru = any(c in q for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    is_en = any(w in q.split() for w in ["what", "how", "when", "where", "price", "brake", "pad", "pads", "plug", "plugs", "oil", "spark", "hours", "contact", "phone", "hello", "hi", "open", "branch", "branches"])

    # 0. Telefon, aloqa yoki call-center so'ralganda
    if any(w in q for w in ["telefon", "nomer", "aloqa", "kontakt", "call center", "call-center", "raqam", "bog'lanish", "телефон", "номер", "связь", "контакт", "контакты", "phone", "contact", "hours", "working"]):
        if is_ru:
            return (
                "📞 <b>Связь и Единый Call-центр Carland:</b>\n\n"
                "• <b>Телефон:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                "• <b>Режим работы:</b> Каждый день <b>с 09:00 до 23:00</b> без выходных!\n"
                "• <b>Филиалы:</b> 15 филиалов по Узбекистану (/filiallar).\n\n"
                "<i>Вы можете позвонить в любое время или посетить наши филиалы!</i>"
            )
        elif is_en:
            return (
                "📞 <b>Carland Call-Center & Working Hours:</b>\n\n"
                "• <b>Phone:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                "• <b>Hours:</b> Every day <b>09:00 - 23:00</b> without days off!\n"
                "• <b>Branches:</b> 15 locations across Uzbekistan (/filiallar).\n\n"
                "<i>Feel free to call anytime or visit our service centers!</i>"
            )
        return (
            "📞 <b>Carland Aloqa va Call-Center:</b>\n\n"
            "• <b>Telefon:</b> <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            "• <b>Ish vaqti:</b> Har kuni <b>09:00 dan 23:00 gacha</b> dam olish kunlarisiz!\n"
            "• <b>Manzillar:</b> 15 ta filialimiz mavjud (/filiallar).\n\n"
            "<i>Istalgan vaqt qo'ng'iroq qilishingiz yoki filiallarimizga tashrif buyurishingiz mumkin!</i>"
        )

    # 1. Tormoz kolodkalari so'ralganda
    if any(w in q for w in ["kolodka", "kalotka", "tormoz", "nakladka", "колодки", "колодка", "brake", "pad"]):
        car_match = "Cobalt" if "cobalt" in q or "кобальт" in q else ("Gentra" if "gentra" in q or "джентра" in q else ("Tracker" if "tracker" in q or "трекер" in q else ("Malibu" if "malibu" in q or "малибу" in q else "avtomobillar")))
        if is_ru:
            return (
                f"🛑 <b>Тормозные колодки для {car_match}:</b>\n\n"
                f"• <b>Fourgreen (Корея):</b> 150 000 - 215 000 сум\n"
                f"• <b>Fourgreen Керамика:</b> 300 000 - 350 000 сум\n"
                f"• <b>Hardron (Премиум Керамика):</b> 350 000 - 365 000 сум\n"
                f"• <b>Brake Master:</b> 150 000 - 170 000 сум\n"
                f"• <b>Japanparts:</b> 170 000 сум\n"
                f"• <b>Platinum:</b> 155 000 сум\n"
                f"• <b>GM Original:</b> 750 000 сум\n\n"
                f"🛠 <i>В сервисах Carland действует профессиональная установка!</i>"
            )
        elif is_en:
            return (
                f"🛑 <b>Brake Pads for {car_match}:</b>\n\n"
                f"• <b>Fourgreen (Korea):</b> 150 000 - 215 000 UZS\n"
                f"• <b>Fourgreen Ceramic:</b> 300 000 - 350 000 UZS\n"
                f"• <b>Hardron (Premium Ceramic):</b> 350 000 - 365 000 UZS\n"
                f"• <b>Brake Master:</b> 150 000 - 170 000 UZS\n"
                f"• <b>Japanparts:</b> 170 000 UZS\n"
                f"• <b>Platinum:</b> 155 000 UZS\n"
                f"• <b>GM Original:</b> 750 000 UZS\n\n"
                f"🛠 <i>Installation service available at Carland centers!</i>"
            )
        return (
            f"🛑 <b>{car_match} uchun tormoz kolodkalari narxlari:</b>\n\n"
            f"• <b>Fourgreen (Koreya):</b> 150 000 - 215 000 so'm\n"
            f"• <b>Fourgreen Keramika:</b> 300 000 - 350 000 so'm\n"
            f"• <b>Hardron (Premium Keramika):</b> 350 000 - 365 000 so'm\n"
            f"• <b>Brake Master:</b> 150 000 - 170 000 so'm\n"
            f"• <b>Japanparts:</b> 170 000 so'm\n"
            f"• <b>Platinum:</b> 155 000 so'm\n"
            f"• <b>GM Original:</b> 750 000 so'm\n\n"
            f"🛠 <i>Carland filiallarida o'rnatish xizmati mavjud!</i>"
        )

    # 2. Svechalar so'ralganda
    if any(w in q for w in ["svecha", "svechalar", "свечи", "свеча", "spark", "plug"]):
        if is_ru:
            return (
                "⚡ <b>Свечи зажигания и замена в Carland:</b>\n\n"
                "• <b>Cobalt, Gentra, Nexia 3, Spark 1.25:</b> ACDelco GM Original (4 шт 160 000 + услуга 70 000 = <b>230 000 сум</b>)\n"
                "• <b>Cobalt (Autozip OE199T10):</b> 4 шт 130 000 + услуга 70 000 = <b>200 000 сум</b>\n"
                "• <b>Matiz, Damas:</b> Autozip (3 шт 105 000 + услуга 50 000 - 60 000 = <b>155 000 - 165 000 сум</b>)\n"
                "• <b>Onix, Tracker 2:</b> ACDelco GM Original (3 шт 350 000 + услуga 60 000 = <b>410 000 сум</b>)\n"
                "• <b>Malibu 2 Turbo:</b> ACDelco GM Original (4 шт 850 000 + услуга 80 000 = <b>930 000 сум</b>)\n"
                "• <b>Captiva 2.4:</b> Torch Iridium (4 шт 340 000 + услуга 80 000 = <b>420 000 сум</b>)\n\n"
                "🛠 <i>В сервисе предоставляется качественная установка с гарантией!</i>"
            )
        elif is_en:
            return (
                "⚡ <b>Spark plugs and replacement at Carland:</b>\n\n"
                "• <b>Cobalt, Gentra, Nexia 3, Spark 1.25:</b> ACDelco GM Original (4 pcs 160 000 + labor 70 000 = <b>230 000 UZS</b>)\n"
                "• <b>Cobalt (Autozip OE199T10):</b> 4 pcs 130 000 + labor 70 000 = <b>200 000 UZS</b>\n"
                "• <b>Matiz, Damas:</b> Autozip (3 pcs 105 000 + labor 50 000 - 60 000 = <b>155 000 - 165 000 UZS</b>)\n"
                "• <b>Onix, Tracker 2:</b> ACDelco GM Original (3 pcs 350 000 + labor 60 000 = <b>410 000 UZS</b>)\n"
                "• <b>Malibu 2 Turbo:</b> ACDelco GM Original (4 pcs 850 000 + labor 80 000 = <b>930 000 UZS</b>)\n"
                "• <b>Captiva 2.4:</b> Torch Iridium (4 pcs 340 000 + labor 80 000 = <b>420 000 UZS</b>)\n\n"
                "🛠 <i>Professional installation available with guarantee!</i>"
            )
        return (
            "⚡ <b>Carland do'konida svechalar va almashtirish narxi:</b>\n\n"
            "• <b>Cobalt, Gentra, Nexia 3, Spark 1.25:</b> ACDelco GM Original (4 dona 160 000 + xizmat 70 000 = <b>230 000 so'm</b>)\n"
            "• <b>Cobalt (Autozip OE199T10):</b> 4 dona 130 000 + xizmat 70 000 = <b>200 000 so'm</b>\n"
            "• <b>Matiz, Damas:</b> Autozip (3 dona 105 000 + xizmat 50 000 - 60 000 = <b>155 000 - 165 000 so'm</b>)\n"
            "• <b>Onix, Tracker 2:</b> ACDelco GM Original (3 dona 350 000 + xizmat 60 000 = <b>410 000 so'm</b>)\n"
            "• <b>Malibu 2 Turbo:</b> ACDelco GM Original (4 dona 850 000 + xizmat 80 000 = <b>930 000 so'm</b>)\n"
            "• <b>Captiva 2.4:</b> Torch Iridium (4 dona 340 000 + xizmat 80 000 = <b>420 000 so'm</b>)\n\n"
            "🛠 <i>Servisimizda kafolatli o'rnatib beriladi!</i>"
        )

    # 3. Filiallar so'ralganda
    if any(w in q for w in ["filial", "manzil", "qayerda", "lokatsiya", "qayerdasiz", "adress", "ish vaqti", "филиал", "филиалы", "адрес", "где вы", "локация", "ориентир", "время работы", "режим работы", "branch", "branches", "location"]):
        if is_ru:
            for b in CARLAND_BRANCHES:
                b_name = b.get("name_ru", b["name"]).lower()
                b_city = b.get("city_ru", b["city"]).lower()
                if any(part in q for part in b_name.split() if len(part) > 3) or b_city in q:
                    return (
                        f"🏢 <b>{b.get('name_ru', b['name'])} ({b.get('city_ru', b['city'])})</b>\n"
                        f"🕒 Режим работы: <b>{b['working_hours']}</b>\n"
                        f"📌 Адрес: {b.get('address_ru', b['address'])}\n"
                        f"📍 Ориентир: <i>{b.get('orientr_ru', b['orientr'])}</i>\n"
                        f"🌐 Локация: {b['location_url']}"
                    )
            res = "📍 <b>Филиалы и режим работы Carland:</b>\n\n"
            for b in CARLAND_BRANCHES[:5]:
                res += f"• <b>{b.get('name_ru', b['name'])}</b> ({b['working_hours']}): {b.get('address_ru', b['address'])} (<a href=\"{b['location_url']}\">Карта</a>)\n"
            res += "\nЧтобы посмотреть все 15 филиалов, введите команду /filiallar!"
            return res
        elif is_en:
            for b in CARLAND_BRANCHES:
                b_name = b.get("name_en", b["name"]).lower()
                b_city = b.get("city_en", b["city"]).lower()
                if any(part in q for part in b_name.split() if len(part) > 3) or b_city in q:
                    return (
                        f"🏢 <b>{b.get('name_en', b['name'])} ({b.get('city_en', b['city'])})</b>\n"
                        f"🕒 Working hours: <b>{b['working_hours']}</b>\n"
                        f"📌 Address: {b.get('address_en', b['address'])}\n"
                        f"📍 Landmark: <i>{b.get('orientr_en', b['orientr'])}</i>\n"
                        f"🌐 Location: {b['location_url']}"
                    )
            res = "📍 <b>Carland Branches & Working Hours:</b>\n\n"
            for b in CARLAND_BRANCHES[:5]:
                res += f"• <b>{b.get('name_en', b['name'])}</b> ({b['working_hours']}): {b.get('address_en', b['address'])} (<a href=\"{b['location_url']}\">Map</a>)\n"
            res += "\nTo view all 15 branches, type /filiallar!"
            return res
        else:
            for b in CARLAND_BRANCHES:
                if b['name'].lower().split()[0] in q or b['city'].lower() in q:
                    return (
                        f"🏢 <b>{b['name']} ({b['city']})</b>\n"
                        f"🕒 Ish vaqti: <b>{b['working_hours']}</b>\n"
                        f"📌 Manzil: {b['address']}\n"
                        f"📍 Mo'ljal: <i>{b['orientr']}</i>\n"
                        f"🌐 Lokatsiya: {b['location_url']}"
                    )
            res = "📍 <b>Carland filiallari va ish vaqtlari:</b>\n\n"
            for b in CARLAND_BRANCHES[:5]:
                res += f"• <b>{b['name']}</b> ({b['working_hours']}): {b['address']} (<a href=\"{b['location_url']}\">Xarita</a>)\n"
            res += "\nBarcha 15 ta filialni ko'rish uchun /filiallar buyrug'ini bosing!"
            return res

    # 4. Maxsus terminlar
    for term, trans in SPECIAL_TERMINOLOGY.items():
        if term.replace("_", " ") in q or term in q:
            return f"💡 <b>Carland ma'lumotnomasi:</b>\nBizda <b>{term}</b> deganda — <code>{trans}</code> nazarda tutiladi. Barcha filiallarimizda sotuvda mavjud!"

    # 5. Mashinalar uchun moy miqdori so'ralganda (Gentra, Cobalt, Nexia va h.k.)
    if any(w in q for w in ["gentra", "lacetti 1.5", "jentra"]):
        return (
            "🛢 <b>Chevrolet Gentra (yangisi) uchun moy hajmlari:</b>\n\n"
            "• <b>Dvigatel (Mator):</b> <b>3.5 litr</b> (5W-30 yoki 5W-40)\n"
            "• <b>Uzatmalar qutisi (Karobka):</b>\n"
            "  ⚡️ <b>Avtomat (AKPP) — Asosiy:</b> <b>7 litr</b> ATF6\n"
            "  🕹 Mexanika (MKPP): 2 litr 75W-90\n"
            "• <b>Filtr almashtirish oralig'i:</b> 25 000 km\n\n"
            "<i>💡 Hozirda mexanika mashinalar kamayganligi sababli, avtomat uzatmalar qutisi (7L ATF6) asosiy hisoblanadi.</i>\n\n"
            "🎁 <b>Gentra uchun Sentabr Aksiya paketlari:</b>\n"
            "• <b>Korelux X500 5w30:</b> 280 000 so'm (Moy + 3 ta filtr BONUS!)\n"
            "• <b>Aveno DX2 5w30:</b> 420 000 so'm (Moy + 3 ta filtr + Sochiq + Osvijitel BONUS!)\n"
            "• <b>Shell Ultra AG 5w30:</b> 475 000 so'm (Moy + 3 ta filtr + Sochiq + Oyna suvi BONUS!)\n\n"
            "🛠 <i>Carland filiallarida mator moyi xarid qilinganda almashtirish MUTLAQO BEPUL! (Faqatgina mator moyi uchun)</i>"
        )

    if "cobalt" in q:
        return (
            "🛢 <b>Chevrolet Cobalt uchun moy hajmlari:</b>\n\n"
            "• <b>Dvigatel (Mator):</b> <b>3.5 litr</b> (0W-20, 5W-30, 5W-40)\n"
            "• <b>Uzatmalar qutisi (Karobka):</b>\n"
            "  ⚡️ <b>Avtomat (AKPP) — Asosiy:</b> <b>7 litr</b> ATF6\n"
            "  🕹 Mexanika (MKPP): 2.5 litr 75W-90\n"
            "• <b>Filtr almashtirish oralig'i:</b> 25 000 km\n\n"
            "🎁 <b>Cobalt uchun Aksiya paketlari:</b>\n"
            "• <b>Korelux X500:</b> 280 000 so'm (3 ta filtr BONUS!)\n"
            "• <b>Shell Ultra AG:</b> 475 000 so'm (3 ta filtr + Oyna suvi + Sochiq BONUS!)\n\n"
            "🛠 <i>Carland filiallarida mator moyi xarid qilinganda almashtirish MUTLAQO BEPUL! (Faqatgina mator moyi uchun)</i>"
        )

    # 6. Karobka va reduktor xizmat haqi
    if any(w in q for w in ["karobka moy", "reduktor", "xizmat haqi", "hizmat haqqi", "alishtirsa", "almashtirsa"]):
        return (
            "⚙️ <b>Karobka va Reduktor moyini almashtirish xizmati:</b>\n\n"
            "• Carland servislarida <b>karobka va reduktor moylarini almashtirishda avtomobil rusumiga qarab xizmat haqi olinadi</b>.\n"
            "• 🛢 <b>Dvigatel (mator) moyi</b> xarid qilinganda esa almashtirish xizmati <b>MUTLAQO BEPUL</b>!\n\n"
            "📞 O'z avtomobilingiz rusumi bo'yicha aniq xizmat narxini bilish uchun: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> yoki /filiallar orqali bog'lanishingiz mumkin."
        )

    # 7. Moylar narxi
    if any(w in q for w in ["moy narxi", "moylar", "mator moyi", "narx", "qancha turadi"]):
        res = "🛢 <b>Carland do'konidagi mashhur moylar narxlari:</b>\n\n"
        for name, d in list(POPULAR_OILS.items())[:5]:
            p = f"{d['price_per_liter']:,}".replace(",", " ")
            res += f"• <b>{name}</b>: {p} so'm / 1L\n<i>{d['desc']}</i>\n\n"
        res += "🛠 <i>Carland servislarida mator moyi xarid qilinganda almashtirish MUTLAQO BEPUL! (Faqatgina mator moyi uchun)</i>"
        return res

    return (
        "Savolingiz qabul qilindi. Carland avtoservisida dvigatel va karobka moylari, "
        "tormoz kolodkalari, svechalar, filtrlar va akkumulyatorlar bo'yicha to'liq xizmat ko'rsatiladi. "
        "Iltimos, mashinangiz rusumi yoki kerakli ehtiyot qismni aniqroq yozing."
    )

