from . import config


def money(n) -> str:
    if n is None:
        return "narx ko'rsatilmagan"
    return f"{int(n):,}".replace(",", " ") + " so'm"


def oil_calc_text(car: dict) -> str:
    lines = [f"🚗 *{car['model']}*", ""]

    lines.append("🔧 *Motor moyi*")
    if car["engine_oil_liters"]:
        lines.append(f"Hajmi: {car['engine_oil_liters']} litr")
        if car["engine_oil_types"]:
            lines.append(f"Tavsiya etilgan tur: {', '.join(car['engine_oil_types'])}")
        lines.append(f"Almashtirish oralig'i: {config.SERVICE_INTERVALS['motor']}")
    else:
        lines.append("Hajmi: bazada ko'rsatilmagan (elektromotor bo'lishi mumkin)")
    lines.append("")

    lines.append("⚙️ *Karobka / Transmissiya*")
    lines.append(car["gearbox_kind"] or "Turi ko'rsatilmagan")
    if car["gearbox_liters"]:
        lines.append(f"Hajmi: {car['gearbox_liters']} litr")
        if car["gearbox_oil_types"]:
            lines.append(f"Tavsiya etilgan tur: {', '.join(car['gearbox_oil_types'])}")
        lines.append(f"Almashtirish oralig'i: {config.SERVICE_INTERVALS['gearbox']}")

    if car["reductor_liters"]:
        lines.append("")
        lines.append("🛞 *Reduktor*")
        lines.append(f"Hajmi: {car['reductor_liters']} litr")
        if car.get("reductor_oil_types"):
            lines.append(f"Tavsiya etilgan tur: {', '.join(car['reductor_oil_types'])}")
        lines.append(f"Almashtirish oralig'i: {config.SERVICE_INTERVALS['reductor']}")

    return "\n".join(lines)


# Foydalanuvchi so'rovi bo'yicha: 4 ta narx darajasi o'rniga 3 ta aniq
# segment — Arzon / Standart / Premium — tavsiya qilinadi.
TIER_LABELS = ("🟢 Arzon", "🟡 Standart", "🔴 Premium")


def _tier_for(index: int, total: int) -> str:
    if total <= 1:
        return TIER_LABELS[0]
    ratio = index / (total - 1)
    if ratio < 1 / 3:
        return TIER_LABELS[0]
    if ratio < 2 / 3:
        return TIER_LABELS[1]
    return TIER_LABELS[2]


def _is_priority_brand(name: str) -> bool:
    """Foydalanuvchi (Carland xo'jayini) talabi bo'yicha: Valvoline (va
    kelajakda config.PRIORITY_BRANDS'ga qo'shilishi mumkin bo'lgan boshqa
    brendlar) har doim "🔴 Premium" segmentida ko'rinib turishi kerak."""
    name_up = (name or "").upper()
    return any(b in name_up for b in config.PRIORITY_BRANDS)


def _pick_representatives(products: list[dict], per_tier: int = 4):
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
    n = len(products)
    if n <= 12:
        # Kichik ro'yxat — sun'iy qisqartirmasdan hammasini ko'rsatamiz
        return [(_tier_for(i, n), p) for i, p in enumerate(products)]
    buckets = {0: [], 1: [], 2: []}
    for i, p in enumerate(products):
        tier_idx = TIER_LABELS.index(_tier_for(i, n))
        buckets[tier_idx].append(p)
    out = []
    for idx in range(3):
        bucket = buckets[idx]
        if idx == 2:
            bucket = _ensure_priority_brand_first(bucket, products)
        for p in bucket[:per_tier]:
            out.append((TIER_LABELS[idx], p))
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


def three_segment_picks(products: list[dict]):
    """Ixcham joylarda (masalan AI erkin-matn chatida) ko'rsatish uchun har
    bir narx segmentidan (Arzon/Standart/Premium) bittadan (segmentdagi eng
    arzoni) tanlaydi — ko'pi bilan 3 ta qator qaytaradi. Premium segmentda
    ustuvor brend (Valvoline) mavjud bo'lsa, aynan o'sha tanlanadi."""
    n = len(products)
    if n == 0:
        return []
    if n <= 3:
        return [(_tier_for(i, n), p) for i, p in enumerate(products)]
    buckets = {0: [], 1: [], 2: []}
    for i, p in enumerate(products):
        idx = TIER_LABELS.index(_tier_for(i, n))
        buckets[idx].append(p)
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
        out.append((TIER_LABELS[idx], chosen))
    return out


def oil_products_text(title: str, liters: float, products: list[dict], filter_price: int | None = None) -> str:
    if not products:
        return f"*{title}*\n\nAfsuski, bu tur moy uchun bazada mos mahsulot topilmadi."
    total_found = len(products)
    lines = [
        f"*{title}* — kerakli hajm: {liters} litr",
        f"_(jami {total_found} xil variant topildi, har narx darajasidan namuna ko'rsatilmoqda)_",
        "",
    ]
    for tier, p in _pick_representatives(products):
        oil_total = p["price"] * liters
        pack = f" ({p['pack_size']})" if p.get("pack_size") else ""
        entry = f"{tier} — *{p['name']}*{pack}\n  {money(p['price'])}/litr × {liters} litr = *{money(oil_total)}*"
        if filter_price is not None:
            grand = oil_total + filter_price
            entry += f"\n  + moy filtri {money(filter_price)} = *{money(grand)}* (to'liq almashtirish)"
        lines.append(entry)
    return "\n\n".join(lines)


def oil_search_results_text(query: str, products: list[dict]) -> str:
    if not products:
        return (
            f"🔎 *\"{query}\"* nomiga mos moy topilmadi.\n"
            "Boshqa nom bilan urinib ko'ring (masalan brend nomi: Valvoline, Castrol, Mobil...)."
        )
    lines = [f"🔎 *\"{query}\"* bo'yicha topilgan moylar:", ""]
    for p in products[:15]:
        pack = f" ({p['pack_size']})" if p.get("pack_size") else ""
        lines.append(f"• {p['name']}{pack} — {money(p['price'])}/litr")
    return "\n".join(lines)


def filter_products_text(title: str, products: list[dict]) -> str:
    if not products:
        return f"*{title}*\n\nBazada mos nom topilmadi. Filialdan so'rab ko'ring."
    lines = [f"*{title}* — topilgan variantlar:", "_(nomi mos kelishini tekshirib tanlang)_", ""]
    for p in products[:12]:
        lines.append(f"• {p['name']} — {money(p['price'])}")
    return "\n".join(lines)


def tires_text(rows: list[dict]) -> str:
    if not rows:
        return "Bazada bu model uchun shina o'lchami topilmadi."
    lines = ["🛞 *Shina o'lchamlari va narxlari*", ""]
    for r in rows:
        lines.append(f"*{r['model']}* ({r['years']})")
        for s in r["sizes"]:
            lines.append(f"\n_{s['size']}_")
            if s["options"]:
                for opt in s["options"]:
                    lines.append(f"  • {opt['name']} — {money(opt['price'])}")
            else:
                lines.append("  (bu o'lcham uchun bazada narx topilmadi)")
        lines.append("")
    return "\n".join(lines).strip()


def batteries_text(data: dict) -> str:
    exact = data.get("exact") or []
    estimated = data.get("estimated") or []
    target_ah = data.get("target_ah")

    if not exact and not estimated:
        return "Bazada akkumulyator ma'lumoti topilmadi."

    lines = ["🔋 *Akkumulyator variantlari*", ""]

    if exact:
        lines.append("✅ *Aniq mos keladigan variantlar:*")
        for r in exact:
            ah = f" — {r['ah']}Ah" if r.get("ah") else ""
            lines.append(f"• {r['name']}{ah} ({r['brand']}) — {money(r['price'])}")
        lines.append("")

    if estimated:
        header = "🧭 *Taxminiy tavsiya" + (f" (~{target_ah}Ah)*" if target_ah else "*")
        lines.append(header)
        lines.append(
            "_(bazada shu model to'g'ridan-to'g'ri ko'rsatilmagan, shuning uchun "
            "dvigatel hajmiga qarab yaqin amperdagi variantlar taklif qilinmoqda — "
            "o'rnatishdan oldin filialda o'lchami/qutb joylashuvini (+/-) tekshirtiring)_"
        )
        for r in estimated:
            ah = f" — {r['ah']}Ah" if r.get("ah") else ""
            lines.append(f"• {r['name']}{ah} ({r['brand']}) — {money(r['price'])}")

    return "\n".join(lines)


def antifreeze_text(rows: list[dict]) -> str:
    if not rows:
        return "Bazada bu model uchun antifriz ma'lumoti topilmadi."
    lines = ["❄️ *Antifriz variantlari*", ""]
    for r in rows:
        kok = f" / ko'k: {money(r['summa_kok'])}" if r.get("summa_kok") else ""
        lines.append(f"• *{r['brand'].split()[0]}* ({r['model']}, {r['liters']} L) — qizil: {money(r['summa_qizil'])}{kok}")
    return "\n".join(lines)


def spark_text(rows: list[dict], product_rows: list[dict] | None = None) -> str:
    product_rows = product_rows or []
    if not rows and not product_rows:
        return "Bazada bu model uchun svecha ma'lumoti topilmadi."
    lines = ["🔌 *Svecha*", ""]
    for r in rows:
        lines.append(f"• {r['model']}: {r['qty']} dona — {money(r['price'])}")
    for r in product_rows:
        lines.append(f"• {r['name']} — {money(r['price'])}")
    return "\n".join(lines)


def brake_pads_text(rows: list[dict]) -> str:
    if not rows:
        return "Bazada bu model uchun tormoz kolodkasi topilmadi. Filialdan so'rab ko'ring."
    lines = ["🔩 *Tormoz kolodkalari* — topilgan variantlar:", "_(nomi mos kelishini tekshirib tanlang)_", ""]
    for r in rows:
        lines.append(f"• {r['name']} — {money(r['price'])}")
    return "\n".join(lines)


def promo_text(rows: list[dict]) -> str:
    if not rows:
        return "Bu model uchun hozircha faol aksiya topilmadi."
    lines = ["🎉 *Faol aksiya paketlari*", ""]
    for r in rows:
        lines.append(f"*{r['package_title']}*")
        lines.append(f"Moy: {r['oil_liters']} litr — {money(r['oil_price'])}")
        for k, v in r["details"].items():
            if v not in (None, "", 0):
                lines.append(f"  {k}: {v}")
        lines.append("")
    return "\n".join(lines).strip()


def branch_text(b: dict) -> str:
    return (
        f"📍 *{b['name']}* ({b['city']})\n\n"
        f"Manzil: {b['address']}\n\n"
        f"Yo'nalish: {b['directions']}"
    )
