"""Oddiy ikki tilli (o'zbek/rus) matnlar lug'ati.

Eslatma: bu botning ASOSIY menyusi va sarlavhalarini tarjima qiladi.
Mahsulot nomlari (baza — ko'pincha ruscha/inglizcha aralash) va batafsil
natija matnlari hozircha faqat o'zbek tilida qoladi, chunki ularning
har birini to'liq tarjima qilish alohida katta ish talab qiladi.
"""

TEXT = {
    "welcome": {
        "uz": (
            "👋 *Carland botiga xush kelibsiz!*\n\n"
            "Bu bot orqali siz:\n"
            "🛢 Mashinangiz uchun aniq moy hajmi va turini hisoblashingiz,\n"
            "🔧 Kerakli mahsulotlarni (filtr, akkumulyator, shina va h.k.) topishingiz,\n"
            "🖼 Motor/karobka/reduktor sxematik infografikasini ko'rishingiz,\n"
            "📍 Eng yaqin filialni topishingiz,\n"
            "💬 AI yordamchidan savol so'rashingiz mumkin.\n\n"
            "Quyidagi menyudan boshlang 👇"
        ),
        "ru": (
            "👋 *Добро пожаловать в бот Carland!*\n\n"
            "Здесь вы можете:\n"
            "🛢 Рассчитать точный объём и тип масла для вашего авто,\n"
            "🔧 Найти нужные товары (фильтры, аккумулятор, шины и т.д.),\n"
            "🖼 Посмотреть схему двигателя/коробки/редуктора,\n"
            "📍 Найти ближайший филиал,\n"
            "💬 Задать вопрос AI-помощнику.\n\n"
            "Начните с меню ниже 👇"
        ),
    },
    "main_menu_title": {"uz": "Bosh menyu:", "ru": "Главное меню:"},
    "menu_oilcalc": {"uz": "🛢 Moy hisoblash", "ru": "🛢 Расчёт масла"},
    "menu_products": {"uz": "🔧 Mahsulotlar", "ru": "🔧 Товары"},
    "menu_info": {"uz": "🖼 Infografika (motor/karobka/reduktor)", "ru": "🖼 Инфографика (двигатель/КПП/редуктор)"},
    "menu_branches": {"uz": "📍 Filiallar", "ru": "📍 Филиалы"},
    "menu_promo": {"uz": "🎉 Aksiyalar", "ru": "🎉 Акции"},
    "menu_ai": {"uz": "💬 AI yordamchidan so'rash", "ru": "💬 Спросить AI-помощника"},
    "menu_admin": {"uz": "📞 Admin bilan bog'lanish", "ru": "📞 Связаться с админом"},
    "menu_lang": {"uz": "🌐 Til / Язык", "ru": "🌐 Til / Язык"},
    "lang_pick": {"uz": "Tilni tanlang:", "ru": "Выберите язык:"},
    "lang_saved": {"uz": "✅ Til o'zbekchaga o'rnatildi.", "ru": "✅ Язык изменён на русский."},
}


def t(key: str, lang: str = "uz") -> str:
    entry = TEXT.get(key, {})
    return entry.get(lang, entry.get("uz", key))
