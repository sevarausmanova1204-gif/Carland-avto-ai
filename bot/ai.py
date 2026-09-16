"""AI yordamchi — Anthropic Claude yoki OpenAI orqali erkin savol-javob.

Xatolikka yo'l qo'ymaslik uchun: modelga bazadan topilgan aniq raqamli
ma'lumotlar (moy hajmi, narx, filial manzili) kontekst sifatida beriladi va
undan faqat shu kontekstdagi raqamlarni ishlatishi, aks holda foydalanuvchini
botning "Moy hisoblash" bo'limiga yo'naltirishi so'raladi — bazada yo'q
raqamni "taxmin qilib" aytmasligi kerak.
"""
from . import config, db

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


def _build_context(user_text: str) -> str:
    parts = []
    words = [w for w in user_text.replace(",", " ").split() if len(w) >= 3]
    seen_cars = set()
    for w in words:
        matches = db.search_cars(w, limit=3)
        for m in matches:
            if m["id"] in seen_cars:
                continue
            seen_cars.add(m["id"])
            car = db.get_car(m["id"])
            parts.append(
                f"- {car['model']}: motor moyi {car['engine_oil_liters']} L "
                f"({', '.join(car['engine_oil_types']) or 'turi ko\'rsatilmagan'}), "
                f"karobka/reduktor {car['gearbox_liters'] or car['reductor_liters'] or '?'} L "
                f"({', '.join(car['gearbox_oil_types']) or 'turi ko\'rsatilmagan'}), "
                f"almashtirish oralig'i: {car['change_interval_km'] or 'ko\'rsatilmagan'} km."
            )
        if len(seen_cars) >= 3:
            break
    if not parts:
        return "(Foydalanuvchi xabarida aniq mashina rusumi topilmadi.)"
    return "MA'LUMOTLAR BAZASIDAN:\n" + "\n".join(parts)


async def ask_ai(user_text: str) -> str:
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
