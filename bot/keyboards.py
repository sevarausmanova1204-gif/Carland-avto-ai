from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from . import brands, config, db
from .i18n import t

ADMIN_USERNAME = "carland_01"


def main_menu(lang: str = "uz", has_recent: bool = False):
    rows = [
        [InlineKeyboardButton(t("menu_oilcalc", lang), callback_data="menu:oilcalc:0")],
        [InlineKeyboardButton(t("menu_products", lang), callback_data="menu:products")],
    ]
    # "So'nggi ko'rilganlar" tugmasi faqat foydalanuvchi allaqachon kamida
    # bitta mashina ko'rgan bo'lsa chiqadi — aks holda bo'sh ro'yxatga olib
    # boradigan foydasiz tugma bilan menyuni cheklamaymiz.
    if has_recent:
        rows.append([InlineKeyboardButton(t("menu_recent", lang), callback_data="menu:recent")])
    rows += [
        [InlineKeyboardButton(t("menu_info", lang), callback_data="menu:info:0")],
        [InlineKeyboardButton(t("menu_branches", lang), callback_data="menu:branches")],
        [InlineKeyboardButton(t("menu_promo", lang), callback_data="menu:promo:0")],
        [InlineKeyboardButton(t("menu_ai", lang), callback_data="menu:ai")],
        [InlineKeyboardButton(t("menu_admin", lang), url=f"https://t.me/{ADMIN_USERNAME}")],
        [InlineKeyboardButton(t("menu_lang", lang), callback_data="menu:lang")],
    ]
    return InlineKeyboardMarkup(rows)


def recent_cars_menu(cars, lang: str = "uz"):
    """`cars` — {"id", "model"} lug'atlar ro'yxati, eng oxirgi ko'rilgani
    birinchi bo'lib keladi."""
    rows = [[InlineKeyboardButton(c["model"], callback_data=f"car:oilcalc:{c['id']}")] for c in cars]
    rows.append([InlineKeyboardButton(t("back_home_btn", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def language_menu():
    rows = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang:uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(rows)


def back_button(target="menu:main", lang: str = "uz"):
    return InlineKeyboardMarkup([[InlineKeyboardButton(t("back_btn", lang), callback_data=target)]])


def _suffix(extra: str) -> str:
    return f":{extra}" if extra else ""


def brand_grid(purpose: str, extra: str = "", lang: str = "uz"):
    """Mashina markalarini 2 ustunli katakchalar shaklida ko'rsatadi (Chevrolet, Kia, ...)."""
    items = brands.brands_with_counts()
    rows = []
    for i in range(0, len(items), 2):
        row = []
        for slug, label, count in items[i:i + 2]:
            cb = f"brand:{purpose}:{slug}:0{_suffix(extra)}"
            row.append(InlineKeyboardButton(f"{label} ({count})", callback_data=cb))
        rows.append(row)
    rows.append([InlineKeyboardButton(t("search_by_name_btn", lang), callback_data=f"search:{purpose}{_suffix(extra)}")])
    rows.append([InlineKeyboardButton(t("back_home_btn", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def brand_car_list_keyboard(purpose: str, brand_slug: str, page: int = 0, extra: str = "", lang: str = "uz"):
    """Tanlangan marka ichidagi mashinalar ro'yxati (sahifalangan)."""
    cars = brands.cars_for_brand(brand_slug)
    per_page = config.CARS_PER_PAGE
    start = page * per_page
    chunk = cars[start:start + per_page]

    rows = []
    for c in chunk:
        cb = f"car:{purpose}:{c['id']}{_suffix(extra)}"
        rows.append([InlineKeyboardButton(c["model"], callback_data=cb)])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"brand:{purpose}:{brand_slug}:{page-1}{_suffix(extra)}"))
    if start + per_page < len(cars):
        nav.append(InlineKeyboardButton("➡️", callback_data=f"brand:{purpose}:{brand_slug}:{page+1}{_suffix(extra)}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(t("back_to_brands_btn", lang), callback_data=f"menu:{purpose}:0{_suffix(extra)}")])
    rows.append([InlineKeyboardButton(t("home_btn", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def products_category_menu(lang: str = "uz"):
    rows = []
    for slug in config.OIL_BROWSE_CATEGORIES:
        rows.append([InlineKeyboardButton(config.oil_browse_label(slug, lang), callback_data=f"oilcat:{slug}")])
    for slug in config.CATEGORY_LABELS:
        rows.append([InlineKeyboardButton(config.category_label(slug, lang), callback_data=f"cat:{slug}:0")])
    for slug in config.SPECIAL_CATEGORIES:
        rows.append([InlineKeyboardButton(config.special_category_label(slug, lang), callback_data=f"special:{slug}")])
    rows.append([InlineKeyboardButton(t("back_home_btn", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)


def oil_origin_menu(slug: str, lang: str = "uz"):
    rows = [
        [InlineKeyboardButton(t("europe_brands_btn", lang), callback_data=f"oilorigin:{slug}:europe:0")],
        [InlineKeyboardButton(t("other_countries_btn", lang), callback_data=f"oilorigin:{slug}:other:0")],
        [InlineKeyboardButton(t("back_products_menu_btn", lang), callback_data="menu:products")],
    ]
    return InlineKeyboardMarkup(rows)


def branches_menu(lang: str = "uz"):
    rows = []
    for b in db.list_branches():
        rows.append([InlineKeyboardButton(f"{b['name']} ({b['city']})", callback_data=f"branch:{b['id']}")])
    rows.append([InlineKeyboardButton(t("back_home_btn", lang), callback_data="menu:main")])
    return InlineKeyboardMarkup(rows)
