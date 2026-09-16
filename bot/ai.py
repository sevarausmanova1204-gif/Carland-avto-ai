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

_ENGINE_KW = ("motor", "matorga", "matoriga", "motoriga", "dvigatel")
_GEARBOX_KW = ("korobka", "karobka", "transmissiya", "akpp", "mkpp", "reduktor")
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
    else:
        liters = car.get("gearbox_liters") or car.get("reductor_liters")
        viscosities = car.get("gearbox_oil_types") or car.get("reductor_oil_types") or []
        category = "gearbox"
        label = "⚙️ Karobka moyi"

    if not liters or not viscosities:
        return f"{label}: bazada hajm/moy turi yo'q, hisoblab bo'lmadi."

    products = db.get_oil_products(viscosities, category)
    origin_note = ""
    if origin:
        products = db.filter_oils_by_origin(products, origin)
        origin_note = ", Yevropa" if origin == "europe" else ", boshqa davlat"

    if not products:
        return f"{label} ({liters} L{origin_note}) — mos moy topilmadi."

    # Matn juda uzun/chalkash bo'lib ketmasligi uchun: aniq tier so'ralganda
    # (arzon/qimmat) FAQAT bitta variant, aks holda ham 3 tadan oshmasin —
    # har biri qisqa, bitta qatorli yozuv sifatida.
    if tier == "cheap":
        chosen, tier_note = [products[0]], ", eng arzon"
    elif tier == "expensive":
        chosen, tier_note = [products[-1]], ", eng yaxshi"
    else:
        chosen, tier_note = products[:3], ""

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
    for target in ("engine", "gearbox"):
        if target not in targets:
            continue
        mods = targets[target]
        blocks.append(_compute_target_calc(car, target, mods.get("origin"), mods.get("tier")))
        blocks.append("")
    blocks.append("_Narxlar joriy narxlar asosida, filialda tasdiqlang._")
    return "\n".join(blocks).strip()


def _build_context(user_text: str) -> str:
    parts = []
    words = [
        w for w in user_text.replace(",", " ").split()
        if len(w) >= 3 and db.normalize_word(w) not in db.GENERIC_WORD_STOPLIST
    ]
    seen_cars = set()
    for w in words:
        matches = db.search_cars(w, limit=3)
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
