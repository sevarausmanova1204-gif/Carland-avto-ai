from . import config


def _L(lang: str, uz: str, ru: str) -> str:
    """Til bo'yicha matn tanlaydi — bu fayldagi BARCHA foydalanuvchiga
    ko'rinadigan matnlar shu orqali tanlanadi, shunda "ichki" (menyu emas,
    balki haqiqiy natija — narx ro'yxati, mashina kartochkasi va h.k.)
    matnlar ham til tanlashga rioya qiladi (avval bular hammasi FAQAT
    o'zbek tilida qattiq yozilgan edi — foydalanuvchi rus tilini tanlagan
    taqdirda ham shu bo'limlar o'zbekcha chiqib qolardi)."""
    return ru if lang == "ru" else uz


def money(n, lang: str = "uz") -> str:
    if n is None:
        return _L(lang, "narx ko'rsatilmagan", "цена не указана")
    unit = _L(lang, "so'm", "сум")
    return f"{int(n):,}".replace(",", " ") + f" {unit}"


def oil_calc_text(car: dict, lang: str = "uz") -> str:
    lines = [f"🚗 *{car['model']}*", ""]

    lines.append(_L(lang, "🔧 *Motor moyi*", "🔧 *Моторное масло*"))
    if car["engine_oil_liters"]:
        lines.append(_L(lang, f"Hajmi: {car['engine_oil_liters']} litr", f"Объём: {car['engine_oil_liters']} л"))
        if car["engine_oil_types"]:
            lines.append(_L(
                lang,
                f"Tavsiya etilgan tur: {', '.join(car['engine_oil_types'])}",
                f"Рекомендуемый тип: {', '.join(car['engine_oil_types'])}",
            ))
        lines.append(_L(
            lang,
            f"Almashtirish oralig'i: {config.SERVICE_INTERVALS['motor']}",
            f"Интервал замены: {config.service_interval_ru('motor')}",
        ))
    else:
        lines.append(_L(
            lang,
            "Hajmi: bazada ko'rsatilmagan (elektromotor bo'lishi mumkin)",
            "Объём не указан в базе (возможно, электромотор)",
        ))
    lines.append("")

    lines.append(_L(lang, "⚙️ *Karobka / Transmissiya*", "⚙️ *Коробка / Трансмиссия*"))
    lines.append(car["gearbox_kind"] or _L(lang, "Turi ko'rsatilmagan", "Тип не указан"))
    if car["gearbox_liters"]:
        lines.append(_L(lang, f"Hajmi: {car['gearbox_liters']} litr", f"Объём: {car['gearbox_liters']} л"))
        if car["gearbox_oil_types"]:
            lines.append(_L(
                lang,
                f"Tavsiya etilgan tur: {', '.join(car['gearbox_oil_types'])}",
                f"Рекомендуемый тип: {', '.join(car['gearbox_oil_types'])}",
            ))
        lines.append(_L(
            lang,
            f"Almashtirish oralig'i: {config.SERVICE_INTERVALS['gearbox']}",
            f"Интервал замены: {config.service_interval_ru('gearbox')}",
        ))

    if car["reductor_liters"]:
        lines.append("")
        lines.append(_L(lang, "🛞 *Reduktor*", "🛞 *Редуктор*"))
        lines.append(_L(lang, f"Hajmi: {car['reductor_liters']} litr", f"Объём: {car['reductor_liters']} л"))
        if car.get("reductor_oil_types"):
            lines.append(_L(
                lang,
                f"Tavsiya etilgan tur: {', '.join(car['reductor_oil_types'])}",
                f"Рекомендуемый тип: {', '.join(car['reductor_oil_types'])}",
            ))
        lines.append(_L(
            lang,
            f"Almashtirish oralig'i: {config.SERVICE_INTERVALS['reductor']}",
            f"Интервал замены: {config.service_interval_ru('reductor')}",
        ))

    return "\n".join(lines)


# Foydalanuvchi so'rovi bo'yicha: 4 ta narx darajasi o'rniga 3 ta aniq
# segment — Arzon / Standart / Premium — tavsiya qilinadi.
TIER_LABELS = ("🟢 Arzon", "🟡 Standart", "🔴 Premium")
TIER_LABELS_RU = ("🟢 Эконом", "🟡 Стандарт", "🔴 Премиум")


def _tier_labels(lang: str) -> tuple:
    return TIER_LABELS_RU if lang == "ru" else TIER_LABELS


def _tier_index(index: int, total: int) -> int:
    if total <= 1:
        return 0
    ratio = index / (total - 1)
    if ratio < 1 / 3:
        return 0
    if ratio < 2 / 3:
        return 1
    return 2


def _tier_for(index: int, total: int, lang: str = "uz") -> str:
    return _tier_labels(lang)[_tier_index(index, total)]


def _is_priority_brand(name: str) -> bool:
    """Foydalanuvchi (Carland xo'jayini) talabi bo'yicha: Valvoline (va
    kelajakda config.PRIORITY_BRANDS'ga qo'shilishi mumkin bo'lgan boshqa
    brendlar) har doim "🔴 Premium" segmentida ko'rinib turishi kerak."""
    name_up = (name or "").upper()
    return any(b in name_up for b in config.PRIORITY_BRANDS)


def _pick_representatives(products: list[dict], per_tier: int = 4, lang: str = "uz"):
    """To'liq (deduplangan, narx bo'yicha o'sish tartibidagi) ro'yxatdan har
    bir narx segmentidan (arzon/standart/premium) bir nechta namuna
    tanlaydi — foydalanuvchiga 50+ ta o'xshash qatorni emas, har segmentdan
    yetarlicha variant ko'rsatish uchun (ro'yxat kichik bo'lsa HAMMASI,
    katta bo'lsa har segmentdan bir nechtadan namuna beriladi). Kerakli
    brend (masalan aniq nomi) ro'yxatda ko'rinmasa, "🔎 Nomi bo'yicha
    qidirish" tugmasi orqali alohida qidirilishi mumkin.

    Premium segmentda ustuvor brend (masalan Valvoline) bo'lsa, u albatta
    ko'rsatiladigan ro'yxatga kiritiladi — uzun ro'yxatda oddiy kesish
    (slicing) natijasida chetda qolib ketmasligi uchun."""
    labels = _tier_labels(lang)
    n = len(products)
    if n <= 12:
        # Kichik ro'yxat — sun'iy qisqartirmasdan hammasini ko'rsatamiz
        return [(labels[_tier_index(i, n)], p) for i, p in enumerate(products)]
    buckets = {0: [], 1: [], 2: []}
    for i, p in enumerate(products):
        buckets[_tier_index(i, n)].append(p)
    out = []
    for idx in range(3):
        bucket = buckets[idx]
        if idx == 2:
            bucket = _ensure_priority_brand_first(bucket, products)
        for p in bucket[:per_tier]:
            out.append((labels[idx], p))
    return out


def _ensure_priority_brand_first(bucket: list[dict], all_products: list[dict]) -> list[dict]:
    """Berilgan (Premium) segment ro'yxatida ustuvor brend mahsuloti bo'lsa,
    uni ro'yxat boshiga chiqaradi (keyingi kesishda (slicing) chetda qolib
    ketmasligi uchun). Segmentning o'zida bunday mahsulot bo'lmasa-yu, lekin
    butun ro'yxatda (boshqa segmentda) mavjud bo'lsa — o'sha eng "premium"ga
    yaqin (eng qimmat) variantni shu segmentga qo'shib qo'yadi, chunki
    foydalanuvchi talabi bo'yicha bu brend narx segmentidan qat'iy nazar
    Premium ro'yxatida ko'rinib turishi shart."""
    priority_in_bucket = [p for p in bucket if _is_priority_brand(p["name"])]
    if priority_in_bucket:
        rest = [p for p in bucket if p not in priority_in_bucket]
        return priority_in_bucket + rest
    priority_anywhere = [p for p in all_products if _is_priority_brand(p["name"])]
    if priority_anywhere:
        best = max(priority_anywhere, key=lambda p: p["price"])
        return [best] + bucket
    return bucket


def three_segment_picks(products: list[dict], lang: str = "uz"):
    """Ixcham joylarda (masalan AI erkin-matn chatida) ko'rsatish uchun har
    bir narx segmentidan (Arzon/Standart/Premium) bittadan (segmentdagi eng
    arzoni) tanlaydi — ko'pi bilan 3 ta qator qaytaradi. Premium segmentda
    ustuvor brend (Valvoline) mavjud bo'lsa, aynan o'sha tanlanadi."""
    labels = _tier_labels(lang)
    n = len(products)
    if n == 0:
        return []
    if n <= 3:
        return [(labels[_tier_index(i, n)], p) for i, p in enumerate(products)]
    buckets = {0: [], 1: [], 2: []}
    for i, p in enumerate(products):
        buckets[_tier_index(i, n)].append(p)
    out = []
    for idx in range(3):
        if not buckets[idx]:
            continue
        if idx == 2:
            priority = [p for p in buckets[idx] if _is_priority_brand(p["name"])]
            if not priority:
                priority = [p for p in products if _is_priority_brand(p["name"])]
            chosen = min(priority, key=lambda p: p["price"]) if priority else buckets[idx][0]
        else:
            chosen = buckets[idx][0]
        out.append((labels[idx], chosen))
    return out


def oil_products_text(
    title: str, liters: float, products: list[dict], filter_price: int | None = None, lang: str = "uz"
) -> str:
    if not products:
        return _L(
            lang,
            f"*{title}*\n\nAfsuski, bu tur moy uchun bazada mos mahsulot topilmadi.",
            f"*{title}*\n\nК сожалению, подходящее масло этого типа не найдено в базе.",
        )
    total_found = len(products)
    lines = [
        f"*{title}* — " + _L(lang, f"kerakli hajm: {liters} litr", f"необходимый объём: {liters} л"),
        _L(
            lang,
            f"_(jami {total_found} xil variant topildi, har narx darajasidan namuna ko'rsatilmoqda)_",
            f"_(всего найдено {total_found} вариантов, показаны примеры по каждому ценовому уровню)_",
        ),
        "",
    ]
    for tier, p in _pick_representatives(products, lang=lang):
        oil_total = p["price"] * liters
        pack = f" ({p['pack_size']})" if p.get("pack_size") else ""
        unit = _L(lang, "litr", "л")
        entry = f"{tier} — *{p['name']}*{pack}\n  {money(p['price'], lang)}/{unit} × {liters} {unit} = *{money(oil_total, lang)}*"
        if filter_price is not None:
            grand = oil_total + filter_price
            entry += "\n  " + _L(
                lang,
                f"+ moy filtri {money(filter_price, lang)} = *{money(grand, lang)}* (to'liq almashtirish)",
                f"+ масляный фильтр {money(filter_price, lang)} = *{money(grand, lang)}* (полная замена)",
            )
        lines.append(entry)
    return "\n\n".join(lines)


def oil_search_results_text(query: str, products: list[dict], lang: str = "uz") -> str:
    if not products:
        return _L(
            lang,
            f"🔎 *\"{query}\"* nomiga mos moy topilmadi.\n"
            "Boshqa nom bilan urinib ko'ring (masalan brend nomi: Valvoline, Castrol, Mobil...).",
            f"🔎 Масло с названием *\"{query}\"* не найдено.\n"
            "Попробуйте другое название (например, бренд: Valvoline, Castrol, Mobil...).",
        )
    lines = [_L(lang, f"🔎 *\"{query}\"* bo'yicha topilgan moylar:", f"🔎 Масла, найденные по запросу *\"{query}\"*:"), ""]
    unit = _L(lang, "litr", "л")
    for p in products[:15]:
        pack = f" ({p['pack_size']})" if p.get("pack_size") else ""
        lines.append(f"• {p['name']}{pack} — {money(p['price'], lang)}/{unit}")
    return "\n".join(lines)


def filter_products_text(title: str, products: list[dict], lang: str = "uz") -> str:
    if not products:
        return _L(
            lang,
            f"*{title}*\n\nBazada mos nom topilmadi. Filialdan so'rab ko'ring.",
            f"*{title}*\n\nПодходящее название не найдено в базе. Уточните в филиале.",
        )
    lines = [
        f"*{title}* — " + _L(lang, "topilgan variantlar:", "найденные варианты:"),
        _L(lang, "_(nomi mos kelishini tekshirib tanlang)_", "_(перед выбором проверьте соответствие названия)_"),
        "",
    ]
    for p in products[:12]:
        lines.append(f"• {p['name']} — {money(p['price'], lang)}")
    return "\n".join(lines)


def tires_text(rows: list[dict], lang: str = "uz") -> str:
    if not rows:
        return _L(lang, "Bazada bu model uchun shina o'lchami topilmadi.", "Размер шин для этой модели не найден в базе.")
    lines = [_L(lang, "🛞 *Shina o'lchamlari va narxlari*", "🛞 *Размеры и цены шин*"), ""]
    for r in rows:
        lines.append(f"*{r['model']}* ({r['years']})")
        for s in r["sizes"]:
            lines.append(f"\n_{s['size']}_")
            if s["options"]:
                for opt in s["options"]:
                    lines.append(f"  • {opt['name']} — {money(opt['price'], lang)}")
            else:
                lines.append("  " + _L(
                    lang,
                    "(bu o'lcham uchun bazada narx topilmadi)",
                    "(цена для этого размера не найдена в базе)",
                ))
        lines.append("")
    return "\n".join(lines).strip()


def batteries_text(data: dict, lang: str = "uz") -> str:
    exact = data.get("exact") or []
    estimated = data.get("estimated") or []
    target_ah = data.get("target_ah")

    if not exact and not estimated:
        return _L(lang, "Bazada akkumulyator ma'lumoti topilmadi.", "Информация об аккумуляторе не найдена в базе.")

    lines = [_L(lang, "🔋 *Akkumulyator variantlari*", "🔋 *Варианты аккумуляторов*"), ""]

    if exact:
        lines.append(_L(lang, "✅ *Aniq mos keladigan variantlar:*", "✅ *Точно подходящие варианты:*"))
        for r in exact:
            ah = f" — {r['ah']}Ah" if r.get("ah") else ""
            lines.append(f"• {r['name']}{ah} ({r['brand']}) — {money(r['price'], lang)}")
        lines.append("")

    if estimated:
        header = _L(lang, "🧭 *Taxminiy tavsiya", "🧭 *Примерная рекомендация") + (f" (~{target_ah}Ah)*" if target_ah else "*")
        lines.append(header)
        lines.append(_L(
            lang,
            "_(bazada shu model to'g'ridan-to'g'ri ko'rsatilmagan, shuning uchun "
            "dvigatel hajmiga qarab yaqin amperdagi variantlar taklif qilinmoqda — "
            "o'rnatishdan oldin filialda o'lchami/qutb joylashuvini (+/-) tekshirtiring)_",
            "_(эта модель напрямую не указана в базе, поэтому предложены варианты с "
            "близким по объёму двигателя амперажем — перед установкой уточните в "
            "филиале размер/расположение полюсов (+/-))_",
        ))
        for r in estimated:
            ah = f" — {r['ah']}Ah" if r.get("ah") else ""
            lines.append(f"• {r['name']}{ah} ({r['brand']}) — {money(r['price'], lang)}")

    return "\n".join(lines)


def antifreeze_text(rows: list[dict], lang: str = "uz") -> str:
    if not rows:
        return _L(lang, "Bazada bu model uchun antifriz ma'lumoti topilmadi.", "Информация об антифризе для этой модели не найдена в базе.")
    lines = [_L(lang, "❄️ *Antifriz variantlari*", "❄️ *Варианты антифриза*"), ""]
    red_label = _L(lang, "qizil", "красный")
    blue_label = _L(lang, "ko'k", "синий")
    for r in rows:
        kok = f" / {blue_label}: {money(r['summa_kok'], lang)}" if r.get("summa_kok") else ""
        lines.append(f"• *{r['brand'].split()[0]}* ({r['model']}, {r['liters']} L) — {red_label}: {money(r['summa_qizil'], lang)}{kok}")
    return "\n".join(lines)


def spark_text(rows: list[dict], product_rows: list[dict] | None = None, lang: str = "uz") -> str:
    product_rows = product_rows or []
    if not rows and not product_rows:
        return _L(lang, "Bazada bu model uchun svecha ma'lumoti topilmadi.", "Информация о свечах для этой модели не найдена в базе.")
    lines = [_L(lang, "🔌 *Svecha*", "🔌 *Свечи*"), ""]
    unit = _L(lang, "dona", "шт")
    for r in rows:
        lines.append(f"• {r['model']}: {r['qty']} {unit} — {money(r['price'], lang)}")
    for r in product_rows:
        lines.append(f"• {r['name']} — {money(r['price'], lang)}")
    return "\n".join(lines)


def brake_pads_text(rows: list[dict], lang: str = "uz") -> str:
    if not rows:
        return _L(
            lang,
            "Bazada bu model uchun tormoz kolodkasi topilmadi. Filialdan so'rab ko'ring.",
            "Тормозные колодки для этой модели не найдены в базе. Уточните в филиале.",
        )
    lines = [
        _L(lang, "🔩 *Tormoz kolodkalari* — topilgan variantlar:", "🔩 *Тормозные колодки* — найденные варианты:"),
        _L(lang, "_(nomi mos kelishini tekshirib tanlang)_", "_(перед выбором проверьте соответствие названия)_"),
        "",
    ]
    for r in rows:
        lines.append(f"• {r['name']} — {money(r['price'], lang)}")
    return "\n".join(lines)


def promo_text(rows: list[dict], lang: str = "uz") -> str:
    if not rows:
        return _L(lang, "Bu model uchun hozircha faol aksiya topilmadi.", "Активных акций для этой модели пока не найдено.")
    lines = [_L(lang, "🎉 *Faol aksiya paketlari*", "🎉 *Активные акционные пакеты*"), ""]
    unit = _L(lang, "litr", "л")
    for r in rows:
        lines.append(f"*{r['package_title']}*")
        lines.append(_L(lang, f"Moy: {r['oil_liters']} {unit} — {money(r['oil_price'], lang)}", f"Масло: {r['oil_liters']} {unit} — {money(r['oil_price'], lang)}"))
        for k, v in r["details"].items():
            if v not in (None, "", 0):
                lines.append(f"  {k}: {v}")
        lines.append("")
    return "\n".join(lines).strip()


def branch_text(b: dict, lang: str = "uz") -> str:
    address_label = _L(lang, "Manzil", "Адрес")
    directions_label = _L(lang, "Yo'nalish", "Как добраться")
    return (
        f"📍 *{b['name']}* ({b['city']})\n\n"
        f"{address_label}: {b['address']}\n\n"
        f"{directions_label}: {b['directions']}"
    )
