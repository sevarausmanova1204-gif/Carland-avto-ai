"""Mashina rusumidan mahsulot katalogida qidirish uchun kalit so'z ajratish.

Muhim eslatma: mahsulot nomlari (filtr, akkumulyator va h.k.) katalogda odatda
faqat model nomi bilan yozilgan ('AIR FILTER ... SORENTO', 'CF COBALT, MALIBU...'),
marka (Kia/Hyundai/Chevrolet) ko'rsatilmaydi. Shu sababli qidiruv kalit so'zi
sifatida asosiy model nomini (marka va qo'shimcha so'zlarsiz) ishlatamiz.
Bu — aniq artikul bo'yicha emas, kalit so'z bo'yicha moslashtirish, shuning
uchun bot javobida "bir nechta variant topildi" deb ko'rsatiladi va yagona
natijani "100% aniq javob" deb da'vo qilmaymiz — mos kelishini xodim/mijoz
mahsulot nomidagi to'liq yozuvdan (masalan "NEXIA 3") tasdiqlaydi.
"""
import re

BRAND_WORDS = {
    "kia", "hyundai", "chevrolet", "daewoo", "byd", "haval", "chery", "changan",
    "dongfeng", "zeekr", "voyah", "leapmotor", "gac", "hongqi", "bmw", "skoda",
    "volkswagen", "lada", "jetour", "bestune", "aito", "ravon", "geely",
}

_TOKEN_RE = re.compile(r"[a-zA-Zʻʼ'`]+|\d+")


def extract_keyword(model: str) -> str:
    text = model.lower()
    text = re.split(r"➤", text)[0]
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\d+(\.\d+)?\s*l\b", " ", text)  # '2l', '1.5l' — dvigatel hajmi belgisi, model raqami emas

    tokens = _TOKEN_RE.findall(text)
    while tokens and tokens[0] in BRAND_WORDS:
        tokens.pop(0)
    if not tokens:
        tokens = _TOKEN_RE.findall(model.lower())
    if not tokens:
        return model.strip().lower()

    base = tokens[0]
    # Faqat modeldan DARHOL keyin (orasida boshqa so'z bo'lmasa) kelgan raqamni
    # qo'shamiz — masalan "tiggo 8", "nexia 3", "k 5". "matiz best 4 slindir"
    # kabi hollarda "best" oralig'idagi so'z bo'lgani uchun raqam qo'shilmaydi.
    if len(tokens) > 1 and tokens[1].isdigit():
        return f"{base} {tokens[1]}"
    return base
