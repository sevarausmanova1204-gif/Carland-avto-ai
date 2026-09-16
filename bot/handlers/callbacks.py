from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .. import brands, config, db, format as fmt, keyboards
from ..i18n import t
from ..infographic import generate_car_infographic
from ..maps import branch_maps_url
from ..matching import extract_keyword


async def route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split(":")
    action = parts[0]
    lang = context.user_data.get("lang", "uz")
    context.user_data.pop("mode", None)  # istalgan menyu bosilsa erkin matn rejimi bekor bo'ladi

    if data == "menu:main":
        await query.edit_message_text(
            t("main_menu_title", lang), reply_markup=keyboards.main_menu(lang)
        )
        return

    if action == "lang":
        new_lang = parts[1]
        context.user_data["lang"] = new_lang
        await query.edit_message_text(
            f"{t('lang_saved', new_lang)}\n\n{t('main_menu_title', new_lang)}",
            reply_markup=keyboards.main_menu(new_lang),
        )
        return

    if action == "menu":
        sub = parts[1]
        if sub == "lang":
            await query.edit_message_text(t("lang_pick", lang), reply_markup=keyboards.language_menu())
            return
        if sub == "products":
            await query.edit_message_text("Qaysi mahsulot turi kerak?", reply_markup=keyboards.products_category_menu())
            return
        if sub == "branches":
            await query.edit_message_text("Filiallardan birini tanlang:", reply_markup=keyboards.branches_menu())
            return
        if sub == "ai":
            context.user_data["mode"] = "ai"
            await query.edit_message_text(
                "💬 AI yordamchi rejimi yoqildi.\nSavolingizni yozing (masalan: \"Cobalt uchun qaysi moy yaxshiroq?\").",
                reply_markup=keyboards.back_button(),
            )
            return
        if sub in ("oilcalc", "info", "promo"):
            title = {
                "oilcalc": "🛢 Moy hisoblash — avval mashina markasini tanlang:",
                "info": "🖼 Infografika — avval mashina markasini tanlang:",
                "promo": "🎉 Aksiya — avval mashina markasini tanlang:",
            }[sub]
            await query.edit_message_text(title, reply_markup=keyboards.brand_grid(sub))
            return
        if sub in ("catcar", "specialcar"):
            slug = parts[3] if len(parts) > 3 else parts[2]
            await query.edit_message_text(
                "Avval mashina markasini tanlang:", reply_markup=keyboards.brand_grid(sub, extra=slug)
            )
            return

    if action == "brand":
        purpose, slug, page = parts[1], parts[2], int(parts[3])
        extra = parts[4] if len(parts) > 4 else ""
        await query.edit_message_text(
            f"*{brands.BRAND_LABELS[slug]}* — mashinani tanlang:",
            reply_markup=keyboards.brand_car_list_keyboard(purpose, slug, page, extra=extra),
            parse_mode="Markdown",
        )
        return

    if action == "cat":
        slug = parts[1]
        if slug in ("chem", "acc"):
            await _render_browse(query, slug, 0)
            return
        await query.edit_message_text(
            "Avval mashina markasini tanlang:", reply_markup=keyboards.brand_grid("catcar", extra=slug)
        )
        return

    if action == "special":
        slug = parts[1]
        await query.edit_message_text(
            "Avval mashina markasini tanlang:", reply_markup=keyboards.brand_grid("specialcar", extra=slug)
        )
        return

    if action == "browse":
        slug, offset = parts[1], int(parts[2])
        await _render_browse(query, slug, offset)
        return

    if action == "oilcat":
        slug = parts[1]
        label, _cats = config.OIL_BROWSE_CATEGORIES[slug]
        await query.edit_message_text(
            f"*{label}* — davlat kelib chiqishini tanlang:", reply_markup=keyboards.oil_origin_menu(slug), parse_mode="Markdown"
        )
        return

    if action == "oilorigin":
        slug, origin, offset = parts[1], parts[2], int(parts[3])
        await _render_oil_browse(query, slug, origin, offset)
        return

    if action == "branch":
        branch = db.get_branch(int(parts[1]))
        url = branch_maps_url(branch)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗺 Yandex Xaritada ochish", url=url)],
            [InlineKeyboardButton("⬅️ Filiallar", callback_data="menu:branches")],
        ])
        await query.edit_message_text(fmt.branch_text(branch), reply_markup=kb, parse_mode="Markdown")
        return

    if action == "car":
        purpose = parts[1]
        car_id = int(parts[2])
        extra = parts[3] if len(parts) > 3 else None
        await _render_car_action(query, purpose, car_id, extra, context)
        return

    if action == "oilprice":
        kind = parts[1]
        car_id = int(parts[2])
        await _render_oil_price(query, kind, car_id)
        return

    if action == "search":
        purpose = parts[1]
        extra = parts[2] if len(parts) > 2 else None
        context.user_data["mode"] = "search"
        context.user_data["search_purpose"] = purpose
        context.user_data["search_extra"] = extra
        await query.edit_message_text(
            "🔎 Mashina nomini yozing (masalan: Cobalt, Sorento, Nexia 3):",
            reply_markup=keyboards.back_button(),
        )
        return


async def _render_browse(query, slug, offset):
    label, category = config.CATEGORY_LABELS[slug]
    items, total = db.browse_category(category, offset=offset, limit=config.PRODUCTS_PER_PAGE)
    lines = [f"*{label}* ({offset + 1}-{offset + len(items)} / {total})", ""]
    for it in items:
        lines.append(f"• {it['name']} — {fmt.money(it['price'])}")
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"browse:{slug}:{max(0, offset - config.PRODUCTS_PER_PAGE)}"))
    if offset + config.PRODUCTS_PER_PAGE < total:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"browse:{slug}:{offset + config.PRODUCTS_PER_PAGE}"))
    rows = [nav] if nav else []
    rows.append([InlineKeyboardButton("⬅️ Mahsulotlar menyusi", callback_data="menu:products")])
    await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")


async def _render_oil_browse(query, slug, origin, offset):
    label, categories = config.OIL_BROWSE_CATEGORIES[slug]
    origin_label = "Yevropa" if origin == "europe" else "Boshqa davlatlar"
    items, total = db.browse_oils_by_origin(categories, origin, offset=offset, limit=config.PRODUCTS_PER_PAGE)
    lines = [f"*{label} — {origin_label}* ({offset + 1}-{offset + len(items)} / {total})", ""]
    for it in items:
        lines.append(f"• {it['name']} — {fmt.money(it['price'])}/litr")
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"oilorigin:{slug}:{origin}:{max(0, offset - config.PRODUCTS_PER_PAGE)}"))
    if offset + config.PRODUCTS_PER_PAGE < total:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"oilorigin:{slug}:{origin}:{offset + config.PRODUCTS_PER_PAGE}"))
    rows = [nav] if nav else []
    rows.append([InlineKeyboardButton("⬅️ Davlat tanlash", callback_data=f"oilcat:{slug}")])
    rows.append([InlineKeyboardButton("🏠 Mahsulotlar menyusi", callback_data="menu:products")])
    await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")


async def _render_car_action(query, purpose, car_id, extra, context):
    car = db.get_car(car_id)
    if not car:
        await query.edit_message_text("Mashina topilmadi.", reply_markup=keyboards.back_button())
        return
    keyword = extract_keyword(car["model"])

    if purpose == "oilcalc":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛢 Motor moyi narxlari", callback_data=f"oilprice:motor:{car_id}")],
            [InlineKeyboardButton("⚙️ Karobka/reduktor moyi narxlari", callback_data=f"oilprice:gearbox:{car_id}")],
            [InlineKeyboardButton("⬅️ Ro'yxatga qaytish", callback_data="menu:oilcalc:0")],
            [InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu:main")],
        ])
        await query.edit_message_text(fmt.oil_calc_text(car), reply_markup=kb, parse_mode="Markdown")
        return

    if purpose == "info":
        await query.edit_message_text(f"🖼 {car['model']} uchun infografika tayyorlanmoqda...")
        png = generate_car_infographic(car)
        await query.message.reply_photo(
            photo=png,
            caption=f"🚗 {car['model']} — motor / karobka / reduktor sxemasi",
            reply_markup=keyboards.back_button("menu:info:0"),
        )
        return

    if purpose == "catcar":
        label, category = config.CATEGORY_LABELS[extra]
        products = db.search_products_by_keyword(keyword, category)
        text = fmt.filter_products_text(f"{label} — {car['model']}", products)
        await query.edit_message_text(text, reply_markup=keyboards.back_button(f"cat:{extra}:0"), parse_mode="Markdown")
        return

    if purpose == "specialcar":
        if extra == "battery":
            rows = db.get_batteries_for_model(car["model"], keyword, car.get("engine_oil_liters"))
            text = fmt.batteries_text(rows)
        elif extra == "antifreeze":
            rows = db.get_antifreeze_for_model(keyword)
            text = fmt.antifreeze_text(rows)
        elif extra == "spark":
            rows = db.get_spark_plug_for_model(keyword)
            product_rows = db.get_spark_plug_products_for_model(keyword)
            text = fmt.spark_text(rows, product_rows)
        elif extra == "tire":
            rows = db.get_tires_for_model(keyword)
            text = fmt.tires_text(rows)
        elif extra == "brake":
            rows = db.get_brake_pads_for_model(keyword)
            text = fmt.brake_pads_text(rows)
        else:
            text = "Noma'lum kategoriya."
        await query.edit_message_text(
            f"🚗 *{car['model']}*\n\n{text}", reply_markup=keyboards.back_button("menu:products"), parse_mode="Markdown"
        )
        return

    if purpose == "promo":
        rows = db.get_promotions_for_model(keyword)
        text = fmt.promo_text(rows)
        await query.edit_message_text(
            f"🚗 *{car['model']}*\n\n{text}", reply_markup=keyboards.back_button("menu:main"), parse_mode="Markdown"
        )
        return


async def _render_oil_price(query, kind, car_id):
    car = db.get_car(car_id)
    if kind == "motor":
        liters = car["engine_oil_liters"]
        types = car["engine_oil_types"]
        products = db.get_oil_products(types, "motor") if liters else []
        filter_matches = db.search_products_by_keyword(extract_keyword(car["model"]), "Oils filters", limit=1)
        filter_price = filter_matches[0]["price"] if filter_matches else None
        text = fmt.oil_products_text(f"🛢 Motor moyi — {car['model']}", liters, products, filter_price) if liters else \
            "Bu model uchun motor moyi hajmi bazada ko'rsatilmagan."
    else:
        # Karobka va reduktor har xil hajm/moy turiga ega bo'lishi mumkin
        # (masalan ba'zi EV/gibrid mashinalarda faqat reduktor bor, karobka
        # yo'q; ba'zilarida ikkalasi ham bor va turlari boshqa-boshqa) —
        # shu sabab ikkalasini alohida-alohida hisoblab, kerak bo'lsa
        # ikkalasini ham ko'rsatamiz.
        parts = []
        if car["gearbox_liters"]:
            products = db.get_oil_products(car["gearbox_oil_types"], "gearbox")
            parts.append(fmt.oil_products_text(f"⚙️ Karobka moyi — {car['model']}", car["gearbox_liters"], products))
        if car["reductor_liters"]:
            products = db.get_oil_products(car["reductor_oil_types"], "gearbox")
            parts.append(fmt.oil_products_text(f"🛞 Reduktor moyi — {car['model']}", car["reductor_liters"], products))
        text = "\n\n---\n\n".join(parts) if parts else "Bu model uchun karobka/reduktor moyi hajmi bazada ko'rsatilmagan."

    await query.edit_message_text(
        text, reply_markup=keyboards.back_button(f"car:oilcalc:{car_id}"), parse_mode="Markdown"
    )
