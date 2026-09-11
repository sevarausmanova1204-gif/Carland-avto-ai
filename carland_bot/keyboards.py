"""
Carland Telegram Bot - Tugmalar Menyusi (Keyboards)
ReplyKeyboardMarkup va InlineKeyboardMarkup
O'zbek, Rus va Ingliz tillarini to'liq qo'llab-quvvatlaydi.
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from car_data import CAR_BRANDS, get_cars_by_category, CARS_DATABASE


def get_language_inline_keyboard(lang: str = "uz", show_back: bool = True) -> InlineKeyboardMarkup:
    """Til tanlash menyusi (O'zbekcha / Русский / English) va Orqaga qaytish tugmasi"""
    back_text = "⬅️ Asosiy menyu"
    if lang == "ru":
        back_text = "⬅️ Главное меню"
    elif lang == "en":
        back_text = "⬅️ Main Menu"

    buttons = [
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang:uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")
        ]
    ]
    if show_back:
        buttons.append([
            InlineKeyboardButton(text=back_text, callback_data="back_to_main")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_main_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari (O'zbek, Rus va Ingliz tillarida)"""
    if lang == "ru":
        keyboard = [
            [
                KeyboardButton(text="🧮 Подбор масла"),
                KeyboardButton(text="📍 Филиалы Carland")
            ],
            [
                KeyboardButton(text="🎁 Сентябрьские акции"),
                KeyboardButton(text="⚡ Экспресс цены")
            ],
            [
                KeyboardButton(text="💬 AI Консультант"),
                KeyboardButton(text="📞 О нас и Контакты")
            ],
            [
                KeyboardButton(text="🌐 Сменить язык"),
                KeyboardButton(text="🧹 Очистить диалог")
            ]
        ]
        placeholder = "Выберите раздел или задайте вопрос..."
    elif lang == "en":
        keyboard = [
            [
                KeyboardButton(text="🧮 Oil Calculator"),
                KeyboardButton(text="📍 Carland Branches")
            ],
            [
                KeyboardButton(text="🎁 September Promos"),
                KeyboardButton(text="⚡ Quick Prices")
            ],
            [
                KeyboardButton(text="💬 AI Consultant"),
                KeyboardButton(text="📞 About & Contacts")
            ],
            [
                KeyboardButton(text="🌐 Change Language"),
                KeyboardButton(text="🧹 Clear Chat")
            ]
        ]
        placeholder = "Select an option or ask a question..."
    else:
        keyboard = [
            [
                KeyboardButton(text="🧮 Moy hisoblash"),
                KeyboardButton(text="📍 Carland filiallari")
            ],
            [
                KeyboardButton(text="🎁 Sentabr Aksiyalari"),
                KeyboardButton(text="⚡ Tezkor narxlar")
            ],
            [
                KeyboardButton(text="💬 AI Maslahatchi"),
                KeyboardButton(text="📞 Biz haqimizda & Aloqa")
            ],
            [
                KeyboardButton(text="🌐 Tilni o'zgartirish"),
                KeyboardButton(text="🧹 Suhbatni tozalash")
            ]
        ]
        placeholder = "Kerakli bo'limni tanlang yoki savolingizni yozing..."

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder=placeholder
    )


def get_branches_links_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Filiallarning Taplink lokatsiyalariga to'g'ridan-to'g'ri havolalar (O'zbek, Rus, Ingliz)"""
    from carland_knowledge import MAIN_TAPLINK_URL
    buttons = []

    # Tilni almashtirish tezkor tugmalari
    buttons.append([
        InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="branches_lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="branches_lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="branches_lang:en")
    ])

    if lang == "ru":
        buttons.append([
            InlineKeyboardButton(text="📍 Тахтапуль", url="https://carlandtaxtapul.taplink.ws"),
            InlineKeyboardButton(text="📍 Чигатай", url="https://carlandchigatoy.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Юнусабад", url="https://carlandyunusobod.taplink.ws"),
            InlineKeyboardButton(text="📍 Луначарский", url="https://carlandlunacharskiy.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Самарканд Дарвоза", url="https://carlandsamarqanddarvoza.taplink.ws"),
            InlineKeyboardButton(text="📍 Домбрабад", url="https://carlanddombiraobod.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Генерал Узаков", url="https://carlandgeneraluzoqov.taplink.ws"),
            InlineKeyboardButton(text="📍 Сергели Индекс", url="https://carlandtashkentindex.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Самарканд", url="https://carlandsamarqand.taplink.ws"),
            InlineKeyboardButton(text="📍 Бухара", url="https://carlandbuxoro.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Чирчик", url="https://carlandchirchiq.taplink.ws"),
            InlineKeyboardButton(text="📍 Карши", url="https://carlandqarshi.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Янгиюль", url="https://carlandyangiyol.taplink.ws"),
            InlineKeyboardButton(text="📍 Алмалык", url="https://carlandolmaliq.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="🌐 Все филиалы (Главная страница)", url=MAIN_TAPLINK_URL)
        ])
        buttons.append([
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")
        ])
    elif lang == "en":
        buttons.append([
            InlineKeyboardButton(text="📍 Takhtapul", url="https://carlandtaxtapul.taplink.ws"),
            InlineKeyboardButton(text="📍 Chigatoy", url="https://carlandchigatoy.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Yunusabad", url="https://carlandyunusobod.taplink.ws"),
            InlineKeyboardButton(text="📍 Lunacharskiy", url="https://carlandlunacharskiy.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Samarkand Darvoza", url="https://carlandsamarqanddarvoza.taplink.ws"),
            InlineKeyboardButton(text="📍 Dombirobod", url="https://carlanddombiraobod.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 General Uzoqov", url="https://carlandgeneraluzoqov.taplink.ws"),
            InlineKeyboardButton(text="📍 Sergeli Index", url="https://carlandtashkentindex.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Samarkand", url="https://carlandsamarqand.taplink.ws"),
            InlineKeyboardButton(text="📍 Bukhara", url="https://carlandbuxoro.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Chirchiq", url="https://carlandchirchiq.taplink.ws"),
            InlineKeyboardButton(text="📍 Karshi", url="https://carlandqarshi.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Yangiyul", url="https://carlandyangiyol.taplink.ws"),
            InlineKeyboardButton(text="📍 Olmaliq", url="https://carlandolmaliq.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="🌐 All Branches (Homepage)", url=MAIN_TAPLINK_URL)
        ])
        buttons.append([
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="📍 Taxtapul", url="https://carlandtaxtapul.taplink.ws"),
            InlineKeyboardButton(text="📍 Chig'atoy", url="https://carlandchigatoy.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Yunusobod", url="https://carlandyunusobod.taplink.ws"),
            InlineKeyboardButton(text="📍 Lunacharskiy", url="https://carlandlunacharskiy.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Samarqand Darvoza", url="https://carlandsamarqanddarvoza.taplink.ws"),
            InlineKeyboardButton(text="📍 Do'mbirobod", url="https://carlanddombiraobod.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 General Uzoqov", url="https://carlandgeneraluzoqov.taplink.ws"),
            InlineKeyboardButton(text="📍 Sergeli Index", url="https://carlandtashkentindex.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Samarqand", url="https://carlandsamarqand.taplink.ws"),
            InlineKeyboardButton(text="📍 Buxoro", url="https://carlandbuxoro.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Chirchiq", url="https://carlandchirchiq.taplink.ws"),
            InlineKeyboardButton(text="📍 Qarshi", url="https://carlandqarshi.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="📍 Yangiyo'l", url="https://carlandyangiyol.taplink.ws"),
            InlineKeyboardButton(text="📍 Olmaliq", url="https://carlandolmaliq.taplink.ws")
        ])
        buttons.append([
            InlineKeyboardButton(text="🌐 Barcha filiallar (Bosh sahifa)", url=MAIN_TAPLINK_URL)
        ])
        buttons.append([
            InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_about_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Biz haqimizda & Aloqa bo'limi uchun tugmalar (til almashtirish va orqaga qaytish bilan)"""
    branch_btn_text = "📍 Filiallar xaritada"
    back_main = "🏠 Asosiy menyu"
    if lang == "ru":
        branch_btn_text = "📍 Филиалы на карте"
        back_main = "🏠 Главное меню"
    elif lang == "en":
        branch_btn_text = "📍 Branches on map"
        back_main = "🏠 Main Menu"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="about_lang:uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="about_lang:ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="about_lang:en")
        ],
        [
            InlineKeyboardButton(text=branch_btn_text, callback_data=f"branches_lang:{lang}")
        ],
        [
            InlineKeyboardButton(text=back_main, callback_data="back_to_main")
        ]
    ])


def get_brands_inline_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Avtomobil markalarini tanlash uchun inline klaviatura"""
    buttons = []
    row = []
    for i, brand in enumerate(CAR_BRANDS, 1):
        row.append(InlineKeyboardButton(text=brand, callback_data=f"brand:{brand}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    back_text = "⬅️ Asosiy menyu"
    if lang == "ru":
        back_text = "⬅️ Главное меню"
    elif lang == "en":
        back_text = "⬅️ Main Menu"

    buttons.append([InlineKeyboardButton(text=back_text, callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cars_inline_keyboard(brand: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """Tanlangan marka bo'yicha modellar ro'yxati"""
    cars = get_cars_by_category(brand)
    buttons = []
    
    for car in cars:
        if "dual_code" in car:
            buttons.append([
                InlineKeyboardButton(
                    text=f"🚘 {car['name']}",
                    callback_data=f"ask_trans:{car['dual_code']}"
                )
            ])
        else:
            car_key = next((k for k, v in CARS_DATABASE.items() if v["name"] == car["name"]), "")
            if car_key:
                buttons.append([
                    InlineKeyboardButton(
                        text=f"🚘 {car['name']}",
                        callback_data=f"car:{car_key}"
                    )
                ])

    back_brands = "⬅️ Markalarga qaytish"
    back_main = "🏠 Asosiy menyu"
    if lang == "ru":
        back_brands = "⬅️ Назад к маркам"
        back_main = "🏠 Главное меню"
    elif lang == "en":
        back_brands = "⬅️ Back to Brands"
        back_main = "🏠 Main Menu"

    buttons.append([
        InlineKeyboardButton(text=back_brands, callback_data="back_to_brands"),
        InlineKeyboardButton(text=back_main, callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_transmission_keyboard(car_code: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """Uzatmalar qutisi turini tanlash (Mexanika yoki Avtomat)"""
    auto_text = "⚡️ Avtomat (AKPP) — Asosiy"
    mech_text = "🕹 Mexanika (MKPP)"
    back_brands = "⬅️ Markalarga qaytish"
    back_main = "🏠 Asosiy menyu"

    if lang == "ru":
        auto_text = "⚡️ Автомат (АКПП) — Рекомендуем"
        mech_text = "🕹 Механика (МКПП)"
        back_brands = "⬅️ Назад к маркам"
        back_main = "🏠 Главное меню"
    elif lang == "en":
        auto_text = "⚡️ Automatic (AT) — Recommended"
        mech_text = "🕹 Manual (MT)"
        back_brands = "⬅️ Back to Brands"
        back_main = "🏠 Main Menu"

    buttons = [
        [
            InlineKeyboardButton(text=auto_text, callback_data=f"trans:{car_code}:avtomat"),
            InlineKeyboardButton(text=mech_text, callback_data=f"trans:{car_code}:mexanika")
        ],
        [
            InlineKeyboardButton(text=back_brands, callback_data="back_to_brands"),
            InlineKeyboardButton(text=back_main, callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_car_result_keyboard(car_key: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """Moy hisoboti ostidagi qo'shimcha amallar va infografika tugmalari"""
    branches_text = "📍 Yaqin filial"
    another_text = "🔄 Boshqa mashina"
    ai_text = "💬 AI maslahat"
    back_main = "🏠 Asosiy menyu"
    
    btn_mator = "🛢 Mator rasmi"
    btn_karobka = "⚙️ Karobka rasmi"
    btn_reduktor = "🔄 Reduktor rasmi"
    btn_filtrlar = "🌪 Filtrlar rasmi"
    btn_umumiy = "📊 To'liq infografika"

    if lang == "ru":
        branches_text = "📍 Найти филиал"
        another_text = "🔄 Другое авто"
        ai_text = "💬 Совет AI"
        back_main = "🏠 Главное меню"
        btn_mator = "🛢 Инфографика мотора"
        btn_karobka = "⚙️ Инфографика КПП"
        btn_reduktor = "🔄 Инфографика редуктора"
        btn_filtrlar = "🌪 Инфографика фильтров"
        btn_umumiy = "📊 Полная инфографика"
    elif lang == "en":
        branches_text = "📍 Find branch"
        another_text = "🔄 Another car"
        ai_text = "💬 Ask AI"
        back_main = "🏠 Main Menu"
        btn_mator = "🛢 Engine Infographic"
        btn_karobka = "⚙️ Gearbox Infographic"
        btn_reduktor = "🔄 Differential Infographic"
        btn_filtrlar = "🌪 Filters Infographic"
        btn_umumiy = "📊 Full Infographic"

    buttons = [
        [
            InlineKeyboardButton(text=btn_mator, callback_data=f"info:{car_key}:mator"),
            InlineKeyboardButton(text=btn_karobka, callback_data=f"info:{car_key}:karobka")
        ],
        [
            InlineKeyboardButton(text=btn_reduktor, callback_data=f"info:{car_key}:reduktor"),
            InlineKeyboardButton(text=btn_filtrlar, callback_data=f"info:{car_key}:filtrlar")
        ],
        [
            InlineKeyboardButton(text=btn_umumiy, callback_data=f"info:{car_key}:umumiy")
        ],
        [
            InlineKeyboardButton(text=branches_text, callback_data=f"branches_lang:{lang}"),
            InlineKeyboardButton(text=another_text, callback_data="back_to_brands")
        ],
        [
            InlineKeyboardButton(text=ai_text, callback_data=f"ask_ai:{car_key}"),
            InlineKeyboardButton(text=back_main, callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_infographic_nav_keyboard(car_key: str, current_type: str = "umumiy", lang: str = "uz") -> InlineKeyboardMarkup:
    """Yuborilgan infografika ostida boshqa rasmlarni tanlash tugmalari"""
    types = [
        ("mator", "🛢 Mator", "🛢 Мотор", "🛢 Engine"),
        ("karobka", "⚙️ Karobka", "⚙️ КПП", "⚙️ Gearbox"),
        ("reduktor", "🔄 Reduktor", "🔄 Редуктор", "🔄 Reductor"),
        ("filtrlar", "🌪 Filtrlar", "🌪 Фильтры", "🌪 Filters"),
        ("umumiy", "📊 Umumiy", "📊 Общая", "📊 Complete")
    ]
    
    buttons = []
    row = []
    for t_code, t_uz, t_ru, t_en in types:
        if t_code == current_type:
            continue
        title = t_uz if lang == "uz" else (t_ru if lang == "ru" else t_en)
        row.append(InlineKeyboardButton(text=title, callback_data=f"info:{car_key}:{t_code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    back_main = "🏠 Asosiy menyu" if lang == "uz" else ("🏠 Главное меню" if lang == "ru" else "🏠 Main Menu")
    another_car = "🔄 Boshqa avto" if lang == "uz" else ("🔄 Другое авто" if lang == "ru" else "🔄 Other car")
    buttons.append([
        InlineKeyboardButton(text=another_car, callback_data="back_to_brands"),
        InlineKeyboardButton(text=back_main, callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
