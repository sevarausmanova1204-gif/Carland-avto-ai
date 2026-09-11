from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Botning asosiy doimiy menyu tugmalari.
    """
    keyboard = [
        [
            KeyboardButton(text="💬 AI Suhbat"),
            KeyboardButton(text="🌍 Global Yangiliklar")
        ],
        [
            KeyboardButton(text="🇪🇸 Ispan tili & Ishlar"),
            KeyboardButton(text="ℹ️ Qo'llanma")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Instagram havolasini yuboring yoki menyuni tanlang..."
    )


def get_spanish_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Ispan tili, Ispaniyada yashash, madaniyat va imkoniyatlar bo'yicha boyitilgan inline menyu.
    """
    inline_keyboard = [
        [
            InlineKeyboardButton(text="💃 Urf-odatlar & Udumlar", callback_data="es_culture"),
            InlineKeyboardButton(text="🏖 Yashash tarzi & Hayot", callback_data="es_lifestyle")
        ],
        [
            InlineKeyboardButton(text="⚡️ Tilni tez o'rganish sirlari", callback_data="es_speed_learning"),
            InlineKeyboardButton(text="📚 Kundalik jonli iboralar", callback_data="es_learning")
        ],
        [
            InlineKeyboardButton(text="💼 Ish, Grantlar & Ta'lim", callback_data="es_jobs_grants"),
            InlineKeyboardButton(text="🎧 Eng sara bepul manbalar", callback_data="es_resources")
        ],
        [
            InlineKeyboardButton(text="🔄 Yangi ma'lumot olish", callback_data="es_refresh")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_video_analysis_keyboard(video_cache_key: str) -> InlineKeyboardMarkup:
    """
    Video yuklab olinganda uning ostida chiqadigan AI tahlil tugmasi.
    """
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="🤖 Videoni AI bilan tahlil qilish",
                callback_data=f"ai_analyze:{video_cache_key}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
