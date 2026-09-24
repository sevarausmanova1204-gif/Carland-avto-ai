from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .. import analytics, brands, config, db, format as fmt, keyboards
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
        analytics.log_event(query.from_user, new_lang, "lang", new_lang)
        await query.edit_message_text(
            f"{t('lang_saved', new_lang)}\n\n{t('main_menu_title', new_lang)}",
            reply_markup=keyboards.main_menu(new_lang),
        )
        return

    if action == "menu":
        sub = parts[1]
        analytics.log_event(query.from_user, lang, "menu", sub)
        if sub == "lang":
            await query.edit_message_text(t("lang_pick", lang), reply_markup=keyboards.language_menu())
            return
        if sub == "products":
            await query.edit_message_text(t("products_menu_title", lang), reply_markup=keyboards.products_category_menu(lang))
            return
        if sub == "branches":
            await query.edit_message_text(t("branches_pick_title", lang), reply_markup=keyboards.branches_menu(lang))
            return
        if sub == "ai":
            context.user_data["mode"] = "ai"
            await query.edit_message_text(
                t("ai_mode_on", lang),
                reply_markup=keyboards.back_button(lang=lang),
            )
            return
        if sub in ("oilcalc", "info", "promo"):
            title_key = {
                "oilcalc": "oilcalc_pick_brand",
                "info": "info_pick_brand",
                "promo": "promo_pick_brand",
            }[sub]
            await query.edit_message_text(t(title_key, lang), reply_markup=keyboards.brand_grid(sub, lang=lang))
            return
        if sub in ("catcar", "specialcar"):
            slug = parts[3] if len(parts) > 3 else parts[2]
            await query.edit_message_text(
                t("pick_brand", lang), reply_markup=keyboards.brand_grid(sub, extra=slug, lang=lang)
            )
            return

    if action == "brand":
        purpose, slug, page = parts[1], parts[2], int(parts[3])
        extra = parts[4] if len(parts) > 4 else ""
        await query.edit_message_text(
            f"*{brands.BRAND_LABELS[slug]}* — {t('choose_car_suffix', lang)}",
            reply_markup=keyboards.brand_car_list_keyboard(purpose, slug, page, extra=extra, lang=lang),
            parse_mode="Markdown",
        )
        return

    if action == "cat":
        slug = parts[1]
        if slug in ("chem", "acc"):
            await _render_browse(query, slug, 0, lang=lang)
            return
        await query.edit_message_text(
            t("pick_brand", lang), reply_markup=keyboards.brand_grid("catcar", extra=slug, lang=lang)
        )
        return

    if action == "special":
        slug = parts[1]
        await query.edit_message_text(
            t("pick_brand", lang), reply_markup=keyboards.brand_grid("specialcar", extra=slug, lang=lang)
        )
        return

    if action == "browse":
        slug, offset = parts[1], int(parts[2])
        await _render_browse(query, slug, offset, lang=lang)
        return

    if action == "oilcat":
        slug = parts[1]
        label = config.oil_browse_label(slug, lang)
        await query.edit_message_text(
            f"*{label}* — {t('select_origin_suffix', lang)}",
            reply_markup=keyboards.oil_origin_menu(slug, lang=lang),
            parse_mode="Markdown",
        )
        return

    if action == "oilorigin":
        slug, origin, offset = parts[1], parts[2], int(parts[3])
        await _render_oil_browse(query, slug, origin, offset, lang=lang)
        return

    if action == "branch":
        branch = db.get_branch(int(parts[1]))
        analytics.log_event(query.from_user, lang, "branch_view", branch.get("name", ""))
        kb_rows = []
        if branch.get("latitude") and branch.get("longitude"):
            kb_rows.append([InlineKeyboardButton(t("send_location_btn", lang), callback_data=f"branchloc:{branch['id']}")])
        url = branch_maps_url(branch)
        kb_rows.append([InlineKeyboardButton(t("open_yandex_maps_btn", lang), url=url)])
        kb_rows.append([InlineKeyboardButton(t("back_to_branches_list_btn", lang), callback_data="menu:branches")])
        await query.edit_message_text(fmt.branch_text(branch, lang), reply_markup=InlineKeyboardMarkup(kb_rows), parse_mode="Markdown")
        return

    if action == "branchloc":
        branch = db.get_branch(int(parts[1]))
        if branch.get("latitude") and branch.get("longitude"):
            await query.message.reply_location(latitude=branch["latitude"], longitude=branch["longitude"])
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
        await _render_oil_price(query, kind, car_id, lang=lang)
        return

    if action == "search":
        purpose = parts[1]
        extra = parts[2] if len(parts) > 2 else None
        context.user_data["mode"] = "search"
        context.user_data["search_purpose"] = purpose
        context.user_data["search_extra"] = extra
        await query.edit_message_text(
            t("search_car_name_prompt", lang),
            reply_markup=keyboards.back_button(lang=lang),
        )
        return

    if action == "oilsearch":
        kind = parts[1]
        car_id = int(parts[2])
        context.user_data["mode"] = "oilsearch"
        context.user_data["oilsearch_kind"] = kind
        context.user_data["oilsearch_car_id"] = car_id
        await query.edit_message_text(
            t("search_oil_name_prompt", lang),
            reply_markup=keyboards.back_button(f"oilprice:{kind}:{car_id}", lang=lang),
        )
        return


async def _render_browse(query, slug, offset, lang: str = "uz"):
    label = config.category_label(slug, lang)
    category = config.category_db(slug)
    items, total = db.browse_category(category, offset=offset, limit=config.PRODUCTS_PER_PAGE)
    lines = [f"*{label}* ({offset + 1}-{offset + len(items)} / {total})", ""]
    for it in items:
        lines.append(f"• {it['name']} — {fmt.money(it['price'], lang)}")
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"browse:{slug}:{max(0, offset - config.PRODUCTS_PER_PAGE)}"))
    if offset + config.PRODUCTS_PER_PAGE < total:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"browse:{slug}:{offset + config.PRODUCTS_PER_PAGE}"))
    rows = [nav] if nav else []
    rows.append([InlineKeyboardButton(t("back_products_menu_btn", lang), callback_data="menu:products")])
    await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")


async def _render_oil_browse(query, slug, origin, offset, lang: str = "uz"):
    label = config.oil_browse_label(slug, lang)
    categories = config.oil_browse_cats(slug)
    origin_label = t("origin_europe_label", lang) if origin == "europe" else t("origin_other_label", lang)
    items, total = db.browse_oils_by_origin(categories, origin, offset=offset, limit=config.PRODUCTS_PER_PAGE)
    lines = [f"*{label} — {origin_label}* ({offset + 1}-{offset + len(items)} / {total})", ""]
    unit = "л" if lang == "ru" else "litr"
    for it in items:
        lines.append(f"• {it['name']} — {fmt.money(it['price'], lang)}/{unit}")
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"oilorigin:{slug}:{origin}:{max(0, offset - config.PRODUCTS_PER_PAGE)}"))
    if offset + config.PRODUCTS_PER_PAGE < total:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"oilorigin:{slug}:{origin}:{offset + config.PRODUCTS_PER_PAGE}"))
    rows = [nav] if nav else []
    rows.append([InlineKeyboardButton(t("back_country_select_btn", lang), callback_data=f"oilcat:{slug}")])
    rows.append([InlineKeyboardButton(t("home_products_menu_btn", lang), callback_data="menu:products")])
    await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")


async def _render_car_action(query, purpose, car_id, extra, context):
    lang = context.user_data.get("lang", "uz")
    car = db.get_car(car_id)
    if not car:
        await query.edit_message_text(t("car_not_found", lang), reply_markup=keyboards.back_button(lang=lang))
        return
    analytics.log_event(query.from_user, lang, "car_view", f"{purpose}:{car['model']}")
    keyword = extract_keyword(car["model"])

    if purpose == "oilcalc":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("motor_oil_prices_btn", lang), callback_data=f"oilprice:motor:{car_id}")],
            [InlineKeyboardButton(t("gearbox_oil_prices_btn", lang), callback_data=f"oilprice:gearbox:{car_id}")],
            [InlineKeyboardButton(t("back_to_list_btn", lang), callback_data="menu:oilcalc:0")],
            [InlineKeyboardButton(t("home_btn", lang), callback_data="menu:main")],
        ])
        await query.edit_message_text(fmt.oil_calc_text(car, lang), reply_markup=kb, parse_mode="Markdown")
        return

    if purpose == "info":
        await query.edit_message_text(t("infographic_preparing", lang).format(model=car["model"]))
        png = generate_car_infographic(car, lang)
        await query.message.reply_photo(
            photo=png,
            caption=t("infographic_caption", lang).format(model=car["model"]),
            reply_markup=keyboards.back_button("menu:info:0", lang=lang),
        )
        return

    if purpose == "catcar":
        label = config.category_label(extra, lang)
        category = config.category_db(extra)
        products = db.search_products_by_keyword(keyword, category)
        text = fmt.filter_products_text(f"{label} — {car['model']}", products, lang)
        await query.edit_message_text(text, reply_markup=keyboards.back_button(f"cat:{extra}:0", lang=lang), parse_mode="Markdown")
        return

    if purpose == "specialcar":
        if extra == "battery":
            rows = db.get_batteries_for_model(car["model"], keyword, car.get("engine_oil_liters"))
            text = fmt.batteries_text(rows, lang)
        elif extra == "antifreeze":
            rows = db.get_antifreeze_for_model(keyword)
            text = fmt.antifreeze_text(rows, lang)
        elif extra == "spark":
            rows = db.get_spark_plug_for_model(keyword)
            product_rows = db.get_spark_plug_products_for_model(keyword)
            text = fmt.spark_text(rows, product_rows, lang)
        elif extra == "tire":
            rows = db.get_tires_for_model(keyword)
            text = fmt.tires_text(rows, lang)
        elif extra == "brake":
            rows = db.get_brake_pads_for_model(keyword)
            text = fmt.brake_pads_text(rows, lang)
        else:
            text = t("unknown_category", lang)
        await query.edit_message_text(
            f"🚗 *{car['model']}*\n\n{text}", reply_markup=keyboards.back_button("menu:products", lang=lang), parse_mode="Markdown"
        )
        return

    if purpose == "promo":
        rows = db.get_promotions_for_model(keyword)
        text = fmt.promo_text(rows, lang)
        await query.edit_message_text(
            f"🚗 *{car['model']}*\n\n{text}", reply_markup=keyboards.back_button("menu:main", lang=lang), parse_mode="Markdown"
        )
        return


async def _render_oil_price(query, kind, car_id, lang: str = "uz"):
    car = db.get_car(car_id)
    analytics.log_event(query.from_user, lang, "oil_price_view", f"{kind}:{car['model']}")
    motor_title = t("motor_oil_title", lang)
    gearbox_title = t("gearbox_oil_title", lang)
    reductor_title = t("reductor_oil_title", lang)
    if kind == "motor":
        liters = car["engine_oil_liters"]
        types = car["engine_oil_types"]
        products = db.get_oil_products(types, "motor") if liters else []
        filter_matches = db.search_products_by_keyword(extract_keyword(car["model"]), "Oils filters", limit=1)
        filter_price = filter_matches[0]["price"] if filter_matches else None
        text = fmt.oil_products_text(f"{motor_title} — {car['model']}", liters, products, filter_price, lang) if liters else \
            t("no_engine_liters", lang)
    else:
        # Karobka (ATF, avtomat/robotlashtirilgan quti) va reduktor (differensial)
        # har xil qism va har xil hajm/moy turiga ega — bittasi mavjud bo'lib,
        # ikkinchisi bazada ko'rsatilmagan bo'lishi mumkin (masalan ba'zi
        # elektromobillarda karobka umuman yo'q). Shu sabab ikkalasini
        # alohida-alohida tekshirib, faqat bazada MA'LUMOTI bor qismi uchun
        # hisoblaymiz, aks holda buni aniq tushuntiramiz — noto'g'ri/taxminiy
        # summa bermaymiz.
        parts = []
        if car["gearbox_liters"]:
            # Mijoz mashina turini (Avtomat/Mexanika/Variator/Robotlashtirilgan)
            # DARHOL ko'rishi kerak — aks holda, masalan, "Cobalt" (Mexanika
            # varianti) va "Cobalt MSM" (Avtomat varianti) kabi bir xil nomga
            # o'xshash, lekin turi boshqa mashinalarda, mijoz nega 75W90
            # (mexanika moyi) chiqqanini tushunmasligi mumkin edi.
            kind_label = f" ({car['gearbox_kind']})" if car.get("gearbox_kind") else ""
            products = db.get_oil_products(car["gearbox_oil_types"], "gearbox")
            parts.append(fmt.oil_products_text(f"{gearbox_title}{kind_label} — {car['model']}", car["gearbox_liters"], products, lang=lang))
        else:
            parts.append(t("no_gearbox_data", lang))

        if car["reductor_liters"]:
            products = db.get_oil_products(car["reductor_oil_types"], "gearbox")
            parts.append(fmt.oil_products_text(f"{reductor_title} — {car['model']}", car["reductor_liters"], products, lang=lang))
        else:
            parts.append(t("no_reductor_data", lang))

        parts.append(config.service_fee_note(lang))
        text = "\n\n---\n\n".join(parts)

    kb_rows = [[InlineKeyboardButton(t("search_oil_by_name_btn", lang), callback_data=f"oilsearch:{kind}:{car_id}")]]
    kb_rows.append([InlineKeyboardButton(t("back_btn", lang), callback_data=f"car:oilcalc:{car_id}")])
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(kb_rows), parse_mode="Markdown"
    )
