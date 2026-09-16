"""AI yordamchi — Anthropic Claude yoki OpenAI orqali erkin savol-javob.

Xatolikka yo'l qo'ymaslik uchun: modelga bazadan topilgan aniq raqamli
ma'lumotlar (moy hajmi, narx, filial manzili) kontekst sifatida beriladi va
undan faqat shu kontekstdagi raqamlarni ishlatishi, aks holda foydalanuvchini
botning "Moy hisoblash" bo'limiga yo'naltirishi so'raladi — bazada yo'q
raqamni "taxmin qilib" aytmasligi kerak.

QO'SHIMCHA FUNKSIYA: agar foydalanuvchi shu erkin-matn chatning o'zida aniq
moy hisob-kitobini so'rasa (masalan: "Captiva ... matoriga yevropa
moylaridan hisoblab ber, karobkasiga budjetniy variantdagi moydan hisoblab
ber"), bu so'rov AI modeliga umuman yubormasdan TO'G'RIDAN-TO'G'RI bazadan
hisoblanadi (_try_deterministic_calc) — shunda javob 100% aniq bo'ladi, AI
hech qanday raqamni "o'ylab topmaydi" va javob tezroq/bepul chiqadi. Bunday
so'rov aniqlanmasa (mashina yoki hisoblash so'zlari topilmasa), oldingi
xatti-harakat — erkin AI suhbati — davom etadi.
"""
import re

from . import config, db
from . import format as fmt

SYSTEM_PROMPT = """Sen "Carland" avtomobil moylari va ehtiyot qismlar do'konining Telegram botidagi AI yordamchisisan.
Faqat o'zbek tilida, do'stona va qisqa javob ber.

QOIDALAR:
1. Moy hajmi, narx, manzil kabi ANIQ raqamlarni FAQAT quyida "MA'LUMOTLAR BAZASIDAN" bo'limida berilgan
   ma'lumotlar asosida ayt. Agar kerakli ma'lumot berilmagan bo'lsa, uni o'zingdan TO'QIB CHIQARMA —
   buning o'rniga foydalanuvchini botning "🛢 Moy hisoblash" yoki "🔧 Mahsulotlar" bo'limidan
   aniq mashina rusumini tanlashga yo'naltir.
2. Umumiy avtomobil/moy bo'yicha bilim savollariga (masalan "sintetik va yarim sintetik moy farqi nima")
   o'z biliming asosida qisqa va foydali javob berishing mumkin.
3. Javobing 6-8 gapdan oshmasin.
"""


# --- Erkin matnda aniq hisob-kitob so'ralganini aniqlash va bazadan hisoblash ---

# Karobka (ATF/avtomat quti) va reduktor (differensial) — IKKI XIL, alohida
# qism (ba'zi mashinalarda ikkalasi ham bor, ba'zilarida faqat bittasi) —
# shu sabab ular ALOHIDA maqsad sifatida aniqlanadi, bittasiga tushib
# qolmaydi (avval "reduktor" so'zi ham "karobka" bilan bitta guruhga tushib,
# faqat bittasi hisoblanardi — bu tuzatildi).
_ENGINE_KW = ("motor", "matorga", "matoriga", "motoriga", "dvigatel")
_GEARBOX_KW = ("korobka", "karobka", "transmissiya", "akpp", "mkpp", "avtomat quti", "avtomat qutisi")
_REDUCTOR_KW = ("reduktor", "reduktorga", "reduktori", "differensial")
_EUROPE_KW = ("yevropa", "evropa", "european")
_OTHER_ORIGIN_KW = ("osiyo", "xitoy", "koreys", "yevropa bo'lmagan", "boshqa davlat")
_CHEAP_KW = ("budjet", "arzon")
_EXPENSIVE_KW = ("qimmat", "premium", "yuqori sifat")
_CALC_TRIGGER_KW = ("hisobla", "necha pul", "qancha", "narxi", "summ", "qiymati")


def _parse_calc_targets(text: str) -> dict:
    """Matnni jumla/qatorlarga bo'lib, har birida motor/karobka so'rovi
    borligini va unga qo'shilgan modifikatorlarni (davlat kelib chiqishi,
    narx darajasi) aniqlaydi. Bir xil maqsad (masalan "motor") bir necha
    qatorda uchrasa, ma'lumotlar birlashtiriladi."""
    chunks = [c for c in re.split(r"[\n.;]+", text) if c.strip()] or [text]
    targets: dict[str, dict] = {}
    for chunk in chunks:
        low = chunk.lower()
        if any(k in low for k in _ENGINE_KW):
            target = "engine"
        elif any(k in low for k in _REDUCTOR_KW):
            target = "reductor"
        elif any(k in low for k in _GEARBOX_KW):
            target = "gearbox"
        else:
            continue
        origin = None
        if any(k in low for k in _EUROPE_KW):
            origin = "europe"
        elif any(k in low for k in _OTHER_ORIGIN_KW):
            origin = "other"
        tier = None
        if any(k in low for k in _CHEAP_KW):
            tier = "cheap"
        elif any(k in low for k in _EXPENSIVE_KW):
            tier = "expensive"
        existing = targets.get(target, {})
        targets[target] = {
            "origin": origin or existing.get("origin"),
            "tier": tier or existing.get("tier"),
        }
    return targets


def _compute_target_calc(car: dict, target: str, origin: str | None, tier: str | None) -> str:
    if target == "engine":
        liters = car.get("engine_oil_liters")
        viscosities = car.get("engine_oil_types") or []
        category = "motor"
        label = "🔧 Motor moyi"
    elif target == "reductor":
        liters = car.get("reductor_liters")
        viscosities = car.get("reductor_oil_types") or []
        category = "gearbox"
        label = "🛞 Reduktor moyi"
    else:  # "gearbox" — karobka (mashinaning o'zida qanday quti bo'lsa, shuning moyi)
        liters = car.get("gearbox_liters")
        viscosities = car.get("gearbox_oil_types") or []
        category = "gearbox"
        # Mashina turini (Avtomat/Mexanika/Variator/Robotlashtirilgan) darhol
        # ko'rsatamiz — aks holda, masalan, "Cobalt" (Mexanika) va "Cobalt MSM"
        # (Avtomat) kabi bir-biriga o'xshash nomli, lekin turi boshqa
        # mashinalarda, mijoz nega 75W90 (mexanika moyi) chiqqanini
        # tushunmay qolishi mumkin edi.
        kind_label = f" ({car['gearbox_kind']})" if car.get("gearbox_kind") else ""
        label = f"⚙️ Karobka moyi{kind_label}"

    if not liters or not viscosities:
        # Karobka va reduktor — alohida qism, ikkalasi ham har doim
        # bo'lavermaydi (masalan ba'zi elektromobillarda karobka umuman
        # yo'q). Noto'g'ri/taxminiy summa bermaslik uchun, faqat bazada
        # ANIQ ma'lumoti bor qism hisoblanadi — bo'lmasa shu aniq aytiladi.
        if target in ("gearbox", "reductor"):
            return f"{label}: bu mashina rusumida bu qism mavjud emas yoki bazada ma'lumot yo'q."
        return f"{label}: bazada hajm/moy turi yo'q, hisoblab bo'lmadi."

    products = db.get_oil_products(viscosities, category)
    origin_note = ""
    if origin:
        products = db.filter_oils_by_origin(products, origin)
        origin_note = ", Yevropa" if origin == "europe" else ", boshqa davlat"

    if not products:
        return f"{label} ({liters} L{origin_note}) — mos moy topilmadi."

    # Aniq tier so'ralganda (arzon/qimmat) FAQAT bitta variant, aks holda
    # 3 ta narx segmentidan (Arzon/Standart/Premium) bittadan — har biri
    # qisqa, bitta qatorli yozuv sifatida.
    if tier == "cheap":
        chosen, tier_note = [products[0]], ", eng arzon"
    elif tier == "expensive":
        chosen, tier_note = [products[-1]], ", eng yaxshi"
    else:
        chosen = [p for _, p in fmt.three_segment_picks(products)]
        tier_note = ""

    lines = [f"{label} — {liters} L{origin_note}{tier_note}:"]
    for p in chosen:
        total = p["price"] * liters
        lines.append(f"• {p['name']} — {fmt.money(p['price'])}/l × {liters} = {fmt.money(total)}")
    if not tier and len(products) > len(chosen):
        lines.append(f"  (yana {len(products) - len(chosen)} ta variant — \"Mahsulotlar\" bo'limida)")
    return "\n".join(lines)


def _try_deterministic_calc(user_text: str) -> str | None:
    low = user_text.lower()
    if not any(k in low for k in _CALC_TRIGGER_KW):
        return None
    targets = _parse_calc_targets(user_text)
    if not targets:
        return None
    car = db.find_car_by_text(user_text)
    if not car:
        return None

    blocks = [f"🚗 *{car['model']}*", ""]
    needs_service_fee = False
    for target in ("engine", "gearbox", "reductor"):
        if target not in targets:
            continue
        if target in ("gearbox", "reductor"):
            needs_service_fee = True
        mods = targets[target]
        blocks.append(_compute_target_calc(car, target, mods.get("origin"), mods.get("tier")))
        blocks.append("")
    if needs_service_fee:
        blocks.append(config.SERVICE_FEE_NOTE)
        blocks.append("")
    blocks.append("_Narxlar joriy narxlar asosida, filialda tasdiqlang._")
    return "\n".join(blocks).strip()


def _norm_visc(v: str | None) -> str:
    return (v or "").upper().replace(" ", "").replace("-", "")


def _try_product_answer(user_text: str) -> str | None:
    """AI erkin-matn chatida "bu brend/mahsulot mos keladimi?", "Valvoline
    bormi?" kabi savollarga LLM ga umuman yubormasdan, TO'G'RIDAN-TO'G'RI
    bazadan javob beradi.

    MUHIM: bu funksiya oldindan sanab chiqilgan aniq brend/mahsulot
    nomlariga BOG'LANMAGAN — matndagi har qanday so'zni (Kirill yozuvi
    lotinchaga o'girilgach, o'zbekcha qo'shimchalar hisobga olingan holda)
    bazadagi `products.name`/`viscosity` ustunlari bo'yicha qidiradi, shu
    sabab bazada mavjud BARCHA brend/mahsulot uchun bab-baravar ishlaydi —
    faqat oldin sinovdan o'tgan bir nechta moy nomlari uchun emas.

    Agar matnda mashina rusumi ham topilsa, topilgan mahsulot(lar)ning
    `viscosity`si o'sha mashinaning motor/karobka/reduktor uchun bazada
    yozilgan talab qilingan turi bilan solishtiriladi va mos keladi/
    kelmasligi aniq aytiladi. Mashina topilmasa, faqat topilgan
    mahsulot(lar) narxi bilan ko'rsatiladi.

    Hech qanday mahsulot/brend so'zi aniqlanmasa, None qaytaradi — bu holda
    chaqiruvchi kod odatdagidek umumiy AI/LLM suhbatiga o'tadi."""
    latin_text = db.transliterate_cyrillic(user_text)
    raw_words = re.split(r"[^\w'ʻʼ]+", latin_text, flags=re.UNICODE)
    candidate_words = [
        w for w in raw_words
        if len(w) >= 3 and db.normalize_word(w) not in db.GENERIC_WORD_STOPLIST
    ]
    if not candidate_words:
        return None

    found: dict[tuple, dict] = {}
    for w in candidate_words:
        for cat in ("motor", "gearbox"):
            for p in db.search_oil_by_name(w, cat):
                key = (cat, p["name"])
                if key not in found:
                    found[key] = {**p, "_cat": cat}

    if not found:
        return None

    products = list(found.values())
    car = db.find_car_by_text(user_text)

    if not car:
        lines = ["🔎 Bazada topilgan mos mahsulotlar:", ""]
        for p in sorted(products, key=lambda r: r["price"])[:10]:
            pack = f" ({p['pack_size']})" if p.get("pack_size") else ""
            lines.append(f"• {p['name']}{pack} — {fmt.money(p['price'])}/litr")
        return "\n".join(lines)

    engine_specs = {_norm_visc(v) for v in (car.get("engine_oil_types") or [])}
    gearbox_specs = {_norm_visc(v) for v in (car.get("gearbox_oil_types") or [])}
    reductor_specs = {_norm_visc(v) for v in (car.get("reductor_oil_types") or [])}

    # Foydalanuvchi aniq qism (motor/karobka/reduktor) nomini aytgan bo'lsa,
    # javob FAQAT o'sha qism bo'yicha beriladi (masalan "Micking 75W90
    # karobkaga to'g'ri keladimi?" — bu savolda motor haqida gap yo'q, shu
    # sabab agar Micking'ning boshqa mahsuloti motorga mos kelsa ham, bu
    # motor mosligi javobda ko'rsatilib, asl savolga (karobka) noto'g'ri
    # ijobiy taassurot berilmasligi kerak). Hech qaysi qism aytilmagan
    # bo'lsa (masalan "Valvoline bu mashinaga to'g'ri keladimi?"), hammasi
    # tekshiriladi.
    low_text = latin_text.lower()
    wants_engine = any(k in low_text for k in _ENGINE_KW)
    wants_gearbox = any(k in low_text for k in _GEARBOX_KW)
    wants_reductor = any(k in low_text for k in _REDUCTOR_KW)
    any_part_specified = wants_engine or wants_gearbox or wants_reductor
    check_engine = wants_engine or not any_part_specified
    check_gearbox = wants_gearbox or not any_part_specified
    check_reductor = wants_reductor or not any_part_specified

    engine_matches = [p for p in products if check_engine and p["_cat"] == "motor" and _norm_visc(p.get("viscosity")) in engine_specs]
    gearbox_matches = [p for p in products if check_gearbox and p["_cat"] == "gearbox" and _norm_visc(p.get("viscosity")) in gearbox_specs]
    reductor_matches = [p for p in products if check_reductor and p["_cat"] == "gearbox" and _norm_visc(p.get("viscosity")) in reductor_specs]

    lines = [f"🚗 *{car['model']}* uchun:"]
    any_match = bool(engine_matches or gearbox_matches or reductor_matches)

    if engine_matches:
        lines += ["", "✅ *Motor moyi* uchun mos keladi:"]
        for p in sorted(engine_matches, key=lambda r: r["price"])[:5]:
            lines.append(f"• {p['name']} — {fmt.money(p['price'])}/litr")
    if gearbox_matches:
        kind_label = f" ({car['gearbox_kind']})" if car.get("gearbox_kind") else ""
        lines += ["", f"✅ *Karobka moyi{kind_label}* uchun mos keladi:"]
        for p in sorted(gearbox_matches, key=lambda r: r["price"])[:5]:
            lines.append(f"• {p['name']} — {fmt.money(p['price'])}/litr")
    if reductor_matches:
        lines += ["", "✅ *Reduktor moyi* uchun mos keladi:"]
        for p in sorted(reductor_matches, key=lambda r: r["price"])[:5]:
            lines.append(f"• {p['name']} — {fmt.money(p['price'])}/litr")

    if not any_match:
        req_parts = []
        if check_engine and engine_specs:
            req_parts.append(f"motorga — {', '.join(sorted(s for s in engine_specs if s))}")
        if check_gearbox and gearbox_specs:
            req_parts.append(f"karobkaga — {', '.join(sorted(s for s in gearbox_specs if s))}")
        if check_reductor and reductor_specs:
            req_parts.append(f"reduktorga — {', '.join(sorted(s for s in reductor_specs if s))}")
        req_text = "; ".join(req_parts) if req_parts else "bazada ko'rsatilmagan"
        # Faqat so'ralgan qismga tegishli toifadagi topilgan mahsulotlarni
        # "boshqa variantlar" sifatida ko'rsatamiz (masalan faqat karobka
        # so'ralgan bo'lsa, motor moylarini bu yerda aralashtirib
        # qo'ymaymiz).
        relevant_products = [
            p for p in products
            if (check_engine and p["_cat"] == "motor")
            or ((check_gearbox or check_reductor) and p["_cat"] == "gearbox")
        ] or products
        lines += [
            "",
            "❌ Topilgan mahsulot(lar) orasida bu mashinaga aniq mos keladigan tur yo'q.",
            f"Bu mashina uchun bazada yozilgan talab qilingan tur: {req_text}.",
            "",
            "Topilgan boshqa variantlar (turi ko'rsatilgan, filialda tekshiring):",
        ]
        for p in sorted(relevant_products, key=lambda r: r["price"])[:5]:
            lines.append(f"• {p['name']} ({p.get('viscosity') or '?'}) — {fmt.money(p['price'])}/litr")
    elif gearbox_matches or reductor_matches:
        lines += ["", config.SERVICE_FEE_NOTE]

    return "\n".join(lines).strip()


def _build_context(user_text: str) -> str:
    parts = []
    # Kirillcha yozuvni ham lotinchaga o'girib olamiz — aks holda bazadagi
    # (lotincha) mashina nomlari bilan solishtirishda hech narsa topilmay
    # qolardi.
    latin_text = db.transliterate_cyrillic(user_text)
    words = [
        w for w in latin_text.replace(",", " ").split()
        if len(w) >= 3 and db.normalize_word(w) not in db.GENERIC_WORD_STOPLIST
    ]
    seen_cars = set()
    for w in words:
        matches = db.search_cars_fuzzy(w, limit=3)
        for m in matches:
            if m["id"] in seen_cars:
                continue
            seen_cars.add(m["id"])
            car = db.get_car(m["id"])
            no_type = "turi ko'rsatilmagan"
            no_km = "ko'rsatilmagan"
            engine_types = ', '.join(car['engine_oil_types']) or no_type
            gearbox_types = ', '.join(car['gearbox_oil_types']) or no_type
            change_km = car['change_interval_km'] or no_km
            parts.append(
                f"- {car['model']}: motor moyi {car['engine_oil_liters']} L "
                f"({engine_types}), "
                f"karobka/reduktor {car['gearbox_liters'] or car['reductor_liters'] or '?'} L "
                f"({gearbox_types}), "
                f"almashtirish oralig'i: {change_km} km."
            )
        if len(seen_cars) >= 3:
            break
    if not parts:
        return "(Foydalanuvchi xabarida aniq mashina rusumi topilmadi.)"
    return "MA'LUMOTLAR BAZASIDAN:\n" + "\n".join(parts)


async def ask_ai(user_text: str) -> str:
    calc_answer = _try_deterministic_calc(user_text)
    if calc_answer:
        return calc_answer

    # Erkin chatda "bu brend/mahsulot mos keladimi?" yoki "shu moy bormi?"
    # kabi savollar — bazadan TO'G'RIDAN-TO'G'RI, LLM'ga yubormasdan javob
    # beriladi (barcha brend/mahsulot uchun umumiy ishlaydi, Kirill yozuvi
    # va o'zbekcha qo'shimchalar bilan yozilgan bo'lsa ham).
    product_answer = _try_product_answer(user_text)
    if product_answer:
        return product_answer

    context_block = _build_context(user_text)
    full_prompt = f"{context_block}\n\nFOYDALANUVCHI SAVOLI: {user_text}"

    if config.AI_PROVIDER == "openai":
        return await _ask_openai(full_prompt)
    return await _ask_anthropic(full_prompt)


async def _ask_anthropic(prompt: str) -> str:
    if not config.ANTHROPIC_API_KEY:
        return "AI yordamchi hozircha sozlanmagan (ANTHROPIC_API_KEY yo'q). Iltimos, .env faylni to'ldiring."
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
    resp = await client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


async def _ask_openai(prompt: str) -> str:
    if not config.OPENAI_API_KEY:
        return "AI yordamchi hozircha sozlanmagan (OPENAI_API_KEY yo'q). Iltimos, .env faylni to'ldiring."
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    resp = await client.chat.completions.create(
        model=config.OPENAI_MODEL,
        max_tokens=600,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return (resp.choices[0].message.content or "").strip()
