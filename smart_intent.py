"""
Carland Telegram Bot - Aqlli Qisqa Savollarni Anglash Moduli (Smart Intent Resolver)
Mijoz qisqa savol yozganda (masalan: "Kobalt R15", "Gentra kalotka", "Tracker svecha", "Kobalt 5w30", "Gentra karobka"):
bazadagi ma'lumotlar asosida mijoz nima xohlayotganini darhol anglab, 0.001 soniyada aniq va professional javob beradi.
O'zbek, Rus va Ingliz tillarini to'liq qo'llab-quvvatlaydi.
"""

import re
from typing import Optional, Dict, Any

# Xalqona / qisqartma avtomobil nomlari sinonimlari
CAR_SYNONYMS = [
    (r'\b(kobalt|koblt|kabal|кобальт|кабальт|кoбалт|cobalt)\b', 'cobalt'),
    (r'\b(jentra|джентра|жентра|gentra)\b', 'gentra'),
    (r'\b(lasetti|laseti|ласетти|ласети|lacetti)\b', 'lacetti'),
    (r'\b(neksiya\s*3|нексия\s*3|nexia\s*3)\b', 'nexia_3'),
    (r'\b(neksiya|нексия|nexiya|nexia)\b', 'nexia'),
    (r'\b(treker\s*2|трекер\s*2|tracker\s*2)\b', 'tracker'),
    (r'\b(treker|trecker|трекер|тракер|tracker)\b', 'tracker'),
    (r'\b(oniks|оникс|onix)\b', 'onix'),
    (r'\b(malyubu\s*2|малибу\s*2|malibu\s*2)\b', 'malibu'),
    (r'\b(malyubu|malubu|малибу|malibu)\b', 'malibu'),
    (r'\b(spark|спарк)\b', 'spark'),
    (r'\b(matis|матиз|matiz)\b', 'matiz'),
    (r'\b(kaptiva|каптива|captiva)\b', 'captiva'),
    (r'\b(damas|дамас)\b', 'damas'),
    (r'\b(labo|лабо)\b', 'labo'),
    (r'\b(chazor|чазор)\b', 'chazor'),
    (r'\b(song|сонг)\b', 'song'),
    (r'\b(yuan\s*up|юань\s*ап)\b', 'yuan_up'),
    (r'\b(yuan\s*plus|юань\s*плюс)\b', 'yuan_plus'),
    (r'\b(yuan|юань)\b', 'yuan'),
    (r'\b(aion\s*s\+?|аион|aion|gac)\b', 'aion'),
    (r'\b(monza|монза)\b', 'monza'),
    (r'\b(equinox|эквинокс)\b', 'equinox'),
    (r'\b(volkswagen\s*id\s*6|volkswagen\s*id6|voltswagen\s*id\s*6|voltswagen\s*id6|volswagen\s*id\s*6|volswagen\s*id6|vw\s*id\s*6|vw\s*id6|id\s*6|id6|ид\s*6|ид6)\b', 'id6'),
    (r'\b(volkswagen\s*id\s*4|volkswagen\s*id4|voltswagen\s*id\s*4|voltswagen\s*id4|volswagen\s*id\s*4|volswagen\s*id4|vw\s*id\s*4|vw\s*id4|id\s*4|id4|ид\s*4|ид4)\b', 'id4'),
    (r'\b(volkswagen|voltswagen|volswagen|vw|фольксваген)\b', 'volkswagen'),
    (r'\b(byd\s*full\s*electr\w*|byd\s*toliq\s*elektr|byd\s*ev|byd\s*elektr)\b', 'byd_ev'),
    (r'\b(chery\s*aiqar\s*eq7|aiqar\s*eq7|aicar\s*eq7|eq7|eq\s*7|aiqar|aicar|айкар)\b', 'eq7'),
    (r'\b(deepal\s*sl03|depal\s*sl03|sl03|sl\s*03|deepal|depal|дипал|депал)\b', 'deepal'),
    (r'\b(traverse|траверс)\b', 'traverse'),
    (r'\b(tahoe|тахо)\b', 'tahoe'),
]

# Avtomobillarning shina (balon) zavod va tavsiya etiladigan o'lchamlari
CAR_TIRE_SPECS: Dict[str, Dict[str, Any]] = {
    "cobalt": {
        "car_name": "Chevrolet Cobalt",
        "primary": ["185/65 R15", "195/65 R15"],
        "alt": ["185/75 R14"],
        "desc_uz": "Cobalt uchun zavod standarti <b>185/65 R15</b>, ammo O'zbekiston sharoitida yumshoqroq va balandroq yurishi uchun ko'pchilik haydovchilar <b>195/65 R15</b> o'lchamini afzal ko'rishadi.",
        "desc_ru": "Для Cobalt заводской стандарт — <b>185/65 R15</b>, однако для более мягкого и комфортного хода большинство водителей выбирают размер <b>195/65 R15</b>.",
        "desc_en": "Factory tire size for Cobalt is <b>185/65 R15</b>, but <b>195/65 R15</b> is the most popular choice for a smoother and higher ride."
    },
    "gentra": {
        "car_name": "Chevrolet Gentra / Lacetti",
        "primary": ["195/55 R15", "195/60 R15", "195/65 R15"],
        "alt": [],
        "desc_uz": "Gentra va Lacetti uchun zavod standarti <b>195/55 R15</b>. Yumshoqroq yurish va diskni asrash uchun ko'pincha <b>195/60 R15</b> yoki <b>195/65 R15</b> o'rnatiladi.",
        "desc_ru": "Заводской размер для Gentra/Lacetti — <b>195/55 R15</b>. Для мягкости и защиты дисков часто ставят <b>195/60 R15</b> или <b>195/65 R15</b>.",
        "desc_en": "Factory size for Gentra/Lacetti is <b>195/55 R15</b>. For a softer ride, <b>195/60 R15</b> or <b>195/65 R15</b> is commonly fitted."
    },
    "lacetti": {
        "car_name": "Chevrolet Lacetti",
        "primary": ["195/55 R15", "195/60 R15", "195/65 R15"],
        "alt": [],
        "desc_uz": "Lacetti uchun zavod standarti <b>195/55 R15</b>, qulaylik uchun <b>195/60 R15</b> yoki <b>195/65 R15</b> tavsiya etiladi.",
        "desc_ru": "Для Lacetti заводской размер — <b>195/55 R15</b>, для комфорта рекомендуются <b>195/60 R15</b> или <b>195/65 R15</b>.",
        "desc_en": "For Lacetti, factory size is <b>195/55 R15</b>, comfort sizes are <b>195/60 R15</b> or <b>195/65 R15</b>."
    },
    "nexia": {
        "car_name": "Chevrolet Nexia 3 / Nexia 2",
        "primary": ["185/60 R14", "185/65 R14", "185/65 R15"],
        "alt": [],
        "desc_uz": "Nexia 3 uchun <b>185/60 R14</b> yoki R15 disklariga <b>185/65 R15</b> shinalari o'rnatiladi.",
        "desc_ru": "Для Nexia 3 подходят шины <b>185/60 R14</b> либо <b>185/65 R15</b>.",
        "desc_en": "Nexia 3 fits <b>185/60 R14</b> or <b>185/65 R15</b> tires."
    },
    "nexia_3": {
        "car_name": "Chevrolet Nexia 3",
        "primary": ["185/60 R14", "185/65 R14", "185/65 R15"],
        "alt": [],
        "desc_uz": "Nexia 3 uchun <b>185/60 R14</b> yoki R15 disklariga <b>185/65 R15</b> shinalari o'rnatiladi.",
        "desc_ru": "Для Nexia 3 подходят шины <b>185/60 R14</b> либо <b>185/65 R15</b>.",
        "desc_en": "Nexia 3 fits <b>185/60 R14</b> or <b>185/65 R15</b> tires."
    },
    "spark": {
        "car_name": "Chevrolet Spark",
        "primary": ["155/70 R14", "165/65 R14", "185/60 R14"],
        "alt": ["175/65 R14"],
        "desc_uz": "Spark uchun zavod standarti <b>155/70 R14</b>, kengroq va yo'lda mustahkam turishi uchun <b>165/65 R14</b> yoki <b>185/60 R14</b> qo'yiladi.",
        "desc_ru": "Заводской размер Spark — <b>155/70 R14</b>, для лучшей устойчивости выбирают <b>165/65 R14</b> или <b>185/60 R14</b>.",
        "desc_en": "Spark factory size is <b>155/70 R14</b>; wider options are <b>165/65 R14</b> or <b>185/60 R14</b>."
    },
    "tracker": {
        "car_name": "Chevrolet Tracker 2",
        "primary": ["215/55 R17"],
        "alt": ["215/60 R17"],
        "desc_uz": "Tracker 2 uchun zavod standarti — <b>215/55 R17</b>.",
        "desc_ru": "Для Tracker 2 заводской размер — <b>215/55 R17</b>.",
        "desc_en": "Factory tire size for Tracker 2 is <b>215/55 R17</b>."
    },
    "onix": {
        "car_name": "Chevrolet Onix",
        "primary": ["195/60 R16", "195/65 R15"],
        "alt": ["185/65 R15"],
        "desc_uz": "Onix uchun <b>195/60 R16</b> (Premier komplektatsiya) yoki <b>195/65 R15</b> shinalari mos keladi.",
        "desc_ru": "Для Onix устанавливаются <b>195/60 R16</b> (Premier) или <b>195/65 R15</b>.",
        "desc_en": "Onix uses <b>195/60 R16</b> (Premier) or <b>195/65 R15</b>."
    },
    "malibu": {
        "car_name": "Chevrolet Malibu 2",
        "primary": ["245/45 R18"],
        "alt": ["245/40 R19"],
        "desc_uz": "Malibu 2 uchun <b>245/45 R18</b> yoki 19-disklarga <b>245/40 R19</b> shinalari o'rnatiladi.",
        "desc_ru": "Для Malibu 2 применяются размеры <b>245/45 R18</b> или <b>245/40 R19</b>.",
        "desc_en": "Malibu 2 uses <b>245/45 R18</b> or <b>245/40 R19</b> tires."
    },
    "damas": {
        "car_name": "Chevrolet Damas / Labo",
        "primary": ["155 R12C"],
        "alt": ["165/70 R12"],
        "desc_uz": "Damas va Labo uchun og'ir yukka mo'ljallangan maxsus kuchaytirilgan <b>155 R12C</b> shinalari tavsiya etiladi.",
        "desc_ru": "Для Damas и Labo рекомендуются усиленные грузовые шины <b>155 R12C</b>.",
        "desc_en": "Damas and Labo require heavy-duty reinforced <b>155 R12C</b> commercial tires."
    },
    "labo": {
        "car_name": "Chevrolet Labo",
        "primary": ["155 R12C"],
        "alt": ["165/70 R12"],
        "desc_uz": "Labo uchun kuchaytirilgan <b>155 R12C</b> yuk shinalari tavsiya etiladi.",
        "desc_ru": "Для Labo рекомендуются усиленные грузовые шины <b>155 R12C</b>.",
        "desc_en": "Labo requires reinforced <b>155 R12C</b> commercial tires."
    },
    "song": {
        "car_name": "BYD Song Plus",
        "primary": ["235/50 R19"],
        "alt": ["235/55 R19"],
        "desc_uz": "BYD Song Plus uchun zavod standarti — <b>235/50 R19</b>.",
        "desc_ru": "Заводской размер для BYD Song Plus — <b>235/50 R19</b>.",
        "desc_en": "Factory size for BYD Song Plus is <b>235/50 R19</b>."
    },
    "chazor": {
        "car_name": "BYD Chazor (Destroyer 05)",
        "primary": ["215/55 R16", "215/50 R17"],
        "alt": [],
        "desc_uz": "BYD Chazor uchun <b>215/55 R16</b> yoki <b>215/50 R17</b> shinalari o'rnatiladi.",
        "desc_ru": "Для BYD Chazor устанавливаются шины <b>215/55 R16</b> или <b>215/50 R17</b>.",
        "desc_en": "BYD Chazor uses <b>215/55 R16</b> or <b>215/50 R17</b>."
    },
    "yuan": {
        "car_name": "BYD Yuan Up",
        "primary": ["215/60 R16", "215/55 R17"],
        "alt": [],
        "desc_uz": "BYD Yuan Up uchun <b>215/60 R16</b> yoki <b>215/55 R17</b> shinalari o'rnatiladi.",
        "desc_ru": "Для BYD Yuan Up подходят шины <b>215/60 R16</b> или <b>215/55 R17</b>.",
        "desc_en": "BYD Yuan Up fits <b>215/60 R16</b> or <b>215/55 R17</b> tires."
    },
    "aion": {
        "car_name": "GAC Aion S+",
        "primary": ["215/55 R17", "225/45 R18"],
        "alt": [],
        "desc_uz": "GAC Aion S+ to'liq elektr sedani uchun <b>215/55 R17</b> yoki <b>225/45 R18</b> shinalari o'rnatiladi.",
        "desc_ru": "Для электромобиля GAC Aion S+ рекомендуются шины <b>215/55 R17</b> или <b>225/45 R18</b>.",
        "desc_en": "GAC Aion S+ electric sedan uses <b>215/55 R17</b> or <b>225/45 R18</b> tires."
    },
    "id4": {
        "car_name": "Volkswagen ID.4",
        "primary": ["235/55 R19", "255/50 R19", "235/50 R20", "255/45 R20"],
        "alt": [],
        "desc_uz": "Volkswagen ID.4 uchun 19-disklarda (oldi <b>235/55 R19</b>, orqa <b>255/50 R19</b>) yoki 20-disklarda (oldi <b>235/50 R20</b>, orqa <b>255/45 R20</b>) shinalari o'rnatiladi.",
        "desc_ru": "Для Volkswagen ID.4 устанавливаются разноширокие шины: 19-дюймовые (перед <b>235/55 R19</b>, зад <b>255/50 R19</b>) либо 20-дюймовые (перед <b>235/50 R20</b>, зад <b>255/45 R20</b>).",
        "desc_en": "Volkswagen ID.4 uses staggered tires: 19-inch (front <b>235/55 R19</b>, rear <b>255/50 R19</b>) or 20-inch (front <b>235/50 R20</b>, rear <b>255/45 R20</b>)."
    },
    "byd_ev": {
        "car_name": "BYD To'liq Elektr (EV)",
        "primary": ["215/55 R17", "215/60 R17", "235/50 R19"],
        "alt": [],
        "desc_uz": "BYD elektr modellari (Yuan Plus, Song EV, Han EV) uchun asosan <b>215/55 R17</b>, <b>215/60 R17</b> yoki <b>235/50 R19</b> shinalari o'rnatiladi.",
        "desc_ru": "Для электромобилей BYD (Yuan Plus, Song EV, Han EV) устанавливаются шины <b>215/55 R17</b>, <b>215/60 R17</b> либо <b>235/50 R19</b>.",
        "desc_en": "BYD electric models (Yuan Plus, Song EV, Han EV) use <b>215/55 R17</b>, <b>215/60 R17</b> or <b>235/50 R19</b> tires."
    }
}

# Avtomobil texnik sig'imlari (Dvigatel va karobka)
CAR_TECHNICAL_SPECS: Dict[str, Dict[str, str]] = {
    "cobalt": {
        "car_name": "Chevrolet Cobalt",
        "engine_oil": "3.5 litr",
        "viscosity": "0W-20 / 5W-30 (Dexos 1 gen 2)",
        "atf": "7 litr ATF6 (Avtomat)",
        "manual": "2.5 litr 75w90 (Mexanika)",
    },
    "gentra": {
        "car_name": "Chevrolet Gentra",
        "engine_oil": "3.5 litr",
        "viscosity": "5W-30 / 5W-40 (Dexos 2)",
        "atf": "7 litr ATF6 (Avtomat)",
        "manual": "2 litr 75w90 (Mexanika)",
    },
    "lacetti": {
        "car_name": "Chevrolet Lacetti 1.6 / 1.8",
        "engine_oil": "3.75 litr",
        "viscosity": "5W-30 / 5W-40",
        "atf": "4 litr ATF (Avtomat)",
        "manual": "1.8 litr 75w90 (Mexanika)",
    },
    "nexia": {
        "car_name": "Chevrolet Nexia 3",
        "engine_oil": "3.5 litr",
        "viscosity": "5W-30 / 5W-40",
        "atf": "7 litr ATF6 (Avtomat)",
        "manual": "2.5 litr 75w90 (Mexanika)",
    },
    "nexia_3": {
        "car_name": "Chevrolet Nexia 3",
        "engine_oil": "3.5 litr",
        "viscosity": "5W-30 / 5W-40",
        "atf": "7 litr ATF6 (Avtomat)",
        "manual": "2.5 litr 75w90 (Mexanika)",
    },
    "spark": {
        "car_name": "Chevrolet Spark",
        "engine_oil": "3.75 litr",
        "viscosity": "5W-30 / 0W-20",
        "atf": "5 litr ATF (Avtomat)",
        "manual": "2.1 litr 75w85 (Mexanika)",
    },
    "tracker": {
        "car_name": "Chevrolet Tracker 2",
        "engine_oil": "4.0 litr",
        "viscosity": "0W-20 (Dexos 1 gen 3)",
        "atf": "7 litr Dexron VI (Avtomat)",
        "manual": "-",
    },
    "onix": {
        "car_name": "Chevrolet Onix",
        "engine_oil": "4.0 litr",
        "viscosity": "0W-20 (Dexos 1 gen 3)",
        "atf": "7 litr Dexron VI (Avtomat)",
        "manual": "2 litr 75w85 (Mexanika)",
    },
    "malibu": {
        "car_name": "Chevrolet Malibu 2",
        "engine_oil": "5.0 litr",
        "viscosity": "5W-30 (Dexos 1 gen 2)",
        "atf": "8.5 litr ATF6 (Avtomat)",
        "manual": "-",
    },
    "damas": {
        "car_name": "Chevrolet Damas",
        "engine_oil": "3.0 litr",
        "viscosity": "10W-40 yarimsintetika",
        "atf": "-",
        "manual": "1.3 litr 75w90 (Mexanika) + 1.3 litr 80w90 (Reduktor)",
    },
    "labo": {
        "car_name": "Chevrolet Labo",
        "engine_oil": "3.0 litr",
        "viscosity": "10W-40 yarimsintetika",
        "atf": "-",
        "manual": "1.3 litr 75w90 (Mexanika) + 1.3 litr 80w90 (Reduktor)",
    },
    "song": {
        "car_name": "BYD Song Plus Gibrid",
        "engine_oil": "3.5 litr",
        "viscosity": "0W-20 maxsus gibrid moyi",
        "atf": "2.0 litr E-CVT reduktor",
        "manual": "-",
    },
    "chazor": {
        "car_name": "BYD Chazor Gibrid",
        "engine_oil": "3.5 litr",
        "viscosity": "0W-20 maxsus gibrid moyi",
        "atf": "2.0 litr E-CVT reduktor",
        "manual": "-",
    },
    "yuan": {
        "car_name": "BYD Yuan Up Gibrid",
        "engine_oil": "4.0 litr",
        "viscosity": "0W-20 gibrid moyi",
        "atf": "2.2 litr EV reduktor moyi",
        "manual": "-",
    },
    "aion": {
        "car_name": "GAC Aion S+ (To'liq Elektr)",
        "engine_oil": "To'liq elektr (Mator moyi mavjud emas)",
        "viscosity": "-",
        "atf": "1.0 litr EV reduktor moyi + 200 000 so'm xizmat",
        "manual": "-",
    },
    "id4": {
        "car_name": "Volkswagen ID.4 (To'liq Elektr)",
        "engine_oil": "To'liq elektr (Dvigatel moyi mavjud emas)",
        "viscosity": "-",
        "atf": "1.0 litr D1 / EV reduktor moyi",
        "manual": "-",
    },
    "id6": {
        "car_name": "Volkswagen ID.6 (To'liq Elektr)",
        "engine_oil": "To'liq elektr (Dvigatel moyi mavjud emas)",
        "viscosity": "-",
        "atf": "Oldi: 600 gr (EV/D2), Orqa: 1 litr (EV/D2)",
        "manual": "-",
    },
    "eq7": {
        "car_name": "Chery Aiqar EQ7 (To'liq Elektr)",
        "engine_oil": "To'liq elektr (Dvigatel moyi mavjud emas)",
        "viscosity": "-",
        "atf": "2.0 litr EV reduktor moyi",
        "manual": "-",
    },
    "deepal": {
        "car_name": "Deepal SL03 Gibrid",
        "engine_oil": "4.0 litr (0w20), Moy filtri: OP 621",
        "viscosity": "0W-20",
        "atf": "1.5 litr EV / D2 reduktor moyi",
        "manual": "-",
    },
    "byd_ev": {
        "car_name": "BYD To'liq Elektr (EV)",
        "engine_oil": "To'liq elektr (Dvigatel moyi mavjud emas)",
        "viscosity": "-",
        "atf": "1.0 litr EV reduktor moyi",
        "manual": "-",
    }
}


def normalize_query_text(text: str) -> str:
    """Xalqona va qisqartma avtomobil nomlarini kanonik nomga o'tkazish"""
    cleaned = text.lower().strip()
    cleaned = re.sub(r'[\'\"`’]', '', cleaned)
    for pattern, rep in CAR_SYNONYMS:
        cleaned = re.sub(pattern, rep, cleaned)
    return cleaned


def detect_car_code(query_norm: str) -> Optional[str]:
    """Matn ichidan avtomobil kodini aniqlash"""
    # Birinchi bo'lib birikmali kalitlarni tekshiramiz
    if re.search(r'\bnexia_3\b', query_norm):
        return 'nexia_3'
    if re.search(r'\byuan_up\b', query_norm):
        return 'yuan'
    for _, rep in CAR_SYNONYMS:
        if re.search(rf'\b{rep}\b', query_norm):
            return 'yuan' if rep.startswith('yuan') else rep
    return None


def is_direct_question(text: str) -> bool:
    """
    Foydalanuvchi matni to'g'ridan-to'g'ri savol, maslahat so'rovi yoki kengaytirilgan
    texnik murojaat ekanligini aniqlaydi.
    Agar True bo'lsa, quruq statik hisobot berilmaydi, balki savol chuqur o'rganilib javob beriladi.
    """
    if not text:
        return False
    t = text.lower().strip()
    if '?' in t:
        return True
        
    # O'zbekcha so'roq yuklamalari (-mi, -misiz, -mikin, -chi, -a):
    # Masalan: bepulmi, qilasizlarmi, bormi, ochiqmisizlar, kelasizmi
    if re.search(r'\b\w+(mi|misiz|misizlar|mikin|mikan|sizlarmi)\b', t):
        return True
        
    question_keywords = [
        'qanday', 'qanaqa', 'qaysi', 'qaysisi', 'qaysilar', 'nega', 'nimaga', 'sabab', 'sababi',
        'qachon', 'qayerda', 'qayerga', 'qayerdan', 'qancha', 'necha', 'nechta', 'nechi',
        'mumkinmi', 'boladimi', "bo'ladimi", 'mumkin', 'kerakmi', 'shartmi', 'shart',
        'farqi', 'farqi nima', 'yaxshimi', 'yaxshiroq', 'maslahat', 'tavsiya', 'yordam',
        'bilmoqchi', 'aytvor', 'aytib', 'tushuntir', 'organib', "o'rganib", 'nima', 'nimani',
        'qilsam', 'yursa', 'yurgan', 'probeg', 'quyish kerak', 'quygan', 'quyilsa',
        'almashtirsa', 'almashtirish kerak', 'rostmi', 'haqiqatdan', 'yeyapti', 'kamayapti',
        'ovoz', 'taqillayapti', 'qizib', 'issiqda', 'qishda', 'yozda', 'gazda', 'metan', 'propan',
        'apparatda', 'apparatsiz', 'tekshirish', 'yuvish', 'tozalash', "o'rnatish", 'ornatish',
        'mos keladimi', 'togrimi', "to'g'rimi", 'berasizmi', 'olasizmi', 'qilasizmi',
        'ochiq', 'yopiq', 'ishlaysizlar', 'yordam bering',
        'как', 'какой', 'какое', 'какая', 'какие', 'почему', 'зачем', 'когда', 'где', 'куда',
        'откуда', 'сколько', 'почем', 'можно', 'можно ли', 'стоит ли', 'нужно ли', 'надо ли',
        'в чем разница', 'разница', 'подскажите', 'посоветуйте', 'совет', 'что лучше', 'подойдет ли',
        'если', 'пробег', 'жрет', 'ест масло', 'жор', 'стучит', 'греется', 'зимой', 'летом',
        'на газу', 'газ', 'пропан', 'метан', 'синтетика', 'полусинтетика', 'аппаратная', 'промывка',
        'правда ли', 'действительно ли', 'что делать',
        'how', 'what', 'why', 'when', 'where', 'which', 'can i', 'should i', 'is it',
        'difference', 'recommend', 'advice', 'better', 'best', 'problem', 'mileage', 'gas',
        'winter', 'summer', 'service'
    ]
    words = re.findall(r'[a-zA-Zа-яА-ЯёЁoʻgʻshch\']+', t)
    for kw in question_keywords:
        if ' ' in kw:
            if kw in t:
                return True
        else:
            if kw in words or re.search(r'\b' + re.escape(kw) + r'\b', t):
                return True

    # 4 tadan ortiq so'z va fe'l/shart qo'shimchasi bo'lsa
    if len(words) >= 4:
        verb_patterns = [r'\w+(sa|yapti|adi|gan|kan)\b']
        for vp in verb_patterns:
            if re.search(vp, t):
                return True
    return False


def resolve_smart_intent(query: str, lang: str = "uz") -> Optional[str]:
    """
    Foydalanuvchi qisqa savol yozganda (masalan: 'Kobalt R15', 'Gentra kalotka', 'Cobalt 5w30', 'Kobalt karobka')
    uning niyatini aniqlab, 0.001 soniyada boy, tushunarli va aniq javob qaytaradi.
    Agar to'g'ridan-to'g'ri savol berilgan bo'lsa, uni to'sib qo'ymasdan None qaytaradi (AI o'rganib javob berishi uchun).
    """
    if is_direct_question(query):
        return None

    q_norm = normalize_query_text(query)
    q_lower = query.lower().strip()

    # 1. SHINA / BALON / RADIUS (masalan: "Kobalt R15", "Gentra r15", "Spark r14", "R15", "balon narxi")
    has_radius = re.search(r'\br\s*(\d{2})\b', q_lower) or re.search(r'\b(\d{2})\s*(lik|likka|radius)\b', q_lower)
    is_tire_word = any(w in q_lower for w in ["shina", "balon", "pokrishka", "shinomontaj", "balansirovka", "колеса", "шины", "покрышка", "шиномонтаж", "tires", "tyre", "tire"])
    has_tire_dimension = re.search(r'\b\d{3}[/\s]\d{2}[/\s]r?\d{2}\b', q_lower)

    if has_radius or is_tire_word or has_tire_dimension:
        radius_val = ""
        if has_radius:
            match = re.search(r'\br\s*(\d{2})\b', q_lower)
            if match:
                radius_val = f"R{match.group(1)}"
            else:
                match2 = re.search(r'\b(\d{2})\s*(lik|likka|radius)\b', q_lower)
                if match2:
                    radius_val = f"R{match2.group(1)}"

        car_code = detect_car_code(q_norm)
        spec = CAR_TIRE_SPECS.get(car_code) if car_code else None

        if spec:
            car_name = spec["car_name"]
            sizes_str = ", ".join([f"<b>{s}</b>" for s in spec["primary"]])
            alt_str = f" (yoki {', '.join(spec['alt'])})" if spec["alt"] else ""
            desc = spec[f"desc_{lang}"] if f"desc_{lang}" in spec else spec["desc_uz"]

            if lang == "ru":
                return (
                    f"🛞 <b>Шины и шиномонтаж для {car_name} ({radius_val or 'Рекомендуемые'}):</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 <b>Рекомендуемые размеры:</b> {sizes_str}{alt_str}\n"
                    f"💡 <i>{desc}</i>\n\n"
                    f"🏷 <b>Ассортимент шин в сети Carland:</b>\n"
                    f"• Charmhoo, Triangle, Lassa, Kumho, Sailun и другие бренды;\n"
                    f"• В наличии летние, зимние и всесезонные шины!\n\n"
                    f"🛠 <b>Услуги автосервиса Carland:</b>\n"
                    f"• Профессиональный шиномонтаж и установка резины;\n"
                    f"• Высокоточная компьютерная балансировка колес;\n"
                    f"• Проверка и подкачка давления в шинах.\n\n"
                    f"📞 Уточнить актуальные цены и наличие нужного размера:\n"
                    f"👉 <a href=\"tel:+998555161616\">+998 55 516 16 16</a> (Call-центр)\n"
                    f"📍 Ближайший филиал: /filiallar"
                )
            elif lang == "en":
                return (
                    f"🛞 <b>Tires and Wheel Service for {car_name} ({radius_val or 'Sizes'}):</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 <b>Recommended Sizes:</b> {sizes_str}{alt_str}\n"
                    f"💡 <i>{desc}</i>\n\n"
                    f"🏷 <b>Tire Brands at Carland:</b>\n"
                    f"• Charmhoo, Triangle, Lassa, Kumho, Sailun, and more;\n"
                    f"• Summer, winter, and all-season tires available!\n\n"
                    f"🛠 <b>Carland Tire Services:</b>\n"
                    f"• Professional mounting and installation;\n"
                    f"• Precise computer wheel balancing;\n"
                    f"• Tire pressure check and adjustment.\n\n"
                    f"📞 Check current pricing and stock:\n"
                    f"👉 <a href=\"tel:+998555161616\">+998 55 516 16 16</a> (Call-center)\n"
                    f"📍 Nearest branch: /filiallar"
                )
            return (
                f"🛞 <b>{car_name} uchun shinalar va shinomontaj ({radius_val or 'Tavsiya etilgan'}):</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 <b>Tavsiya qilinadigan o'lchamlar:</b> {sizes_str}{alt_str}\n"
                f"💡 <i>{desc}</i>\n\n"
                f"🏷 <b>Carland markazlarida mavjud shinalar:</b>\n"
                f"• Charmhoo, Triangle, Lassa, Kumho, Sailun va boshqa brendlar;\n"
                f"• Yozgi, qishki va barcha faslga mos (all-season) shinalar!\n\n"
                f"🛠 <b>Carland Shinomontaj xizmatlari:</b>\n"
                f"• Shinalarni sifatli o'rnatish va almashtirish;\n"
                f"• G'ildiraklarni kompyuterda aniq balansirovka qilish;\n"
                f"• Shina bosimini tekshirish va to'g'rilash.\n\n"
                f"📞 Aniq narxlar va qoldiqni bilish uchun:\n"
                f"👉 <a href=\"tel:+998555161616\">+998 55 516 16 16</a> (Call-center)\n"
                f"📍 O'zingizga yaqin filial: /filiallar"
            )
        else:
            rad_title = radius_val if radius_val else "avtomobil"
            if lang == "ru":
                return (
                    f"🛞 <b>Шины {rad_title} и шиномонтаж в Carland:</b>\n\n"
                    f"• В филиалах Carland представлен широкий выбор шин от R12 до R20 (Charmhoo, Triangle, Lassa, Kumho, Sailun);\n"
                    f"• Действует профессиональный шиномонтаж и балансировка колес!\n\n"
                    f"📞 Уточнить размер и цену для вашего авто: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                    f"📍 Адреса филиалов: /filiallar"
                )
            elif lang == "en":
                return (
                    f"🛞 <b>Tires {rad_title} and Tire Service at Carland:</b>\n\n"
                    f"• Carland offers wide selection of tires from R12 to R20 (Charmhoo, Triangle, Lassa, Kumho, Sailun);\n"
                    f"• Professional mounting and computer balancing available!\n\n"
                    f"📞 Check size and price: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                    f"📍 Branch locations: /filiallar"
                )
            return (
                f"🛞 <b>{rad_title} shinalari va shinomontaj Carland da:</b>\n\n"
                f"• Carland filiallarida R12 dan R20 gacha barcha o'lchamdagi sifatli shinalar mavjud (Charmhoo, Triangle, Lassa, Kumho, Sailun);\n"
                f"• Professional shinomontaj va kompyuter balansirovkasi xizmati yo'lga qo'yilgan!\n\n"
                f"📞 O'z avtomobilingiz uchun aniq narxni bilish: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"📍 Filiallar manzillari: /filiallar"
            )

    # 2. TORMOZ KOLODKALARI (masalan: "Kobalt kalotka", "Gentra tormoz", "Fourgreen", "Hardron")
    if any(w in q_lower for w in ["kolodka", "kalotka", "tormoz", "nakladka", "колодки", "колодка", "brake", "fourgreen", "hardron"]):
        car_code = detect_car_code(q_norm)
        car_title = "Chevrolet Cobalt" if car_code == "cobalt" else ("Chevrolet Gentra" if car_code == "gentra" else ("Chevrolet Tracker 2" if car_code == "tracker" else "avtomobillar"))
        if lang == "ru":
            return (
                f"🛑 <b>Тормозные колодки для {car_title} в наличии:</b>\n\n"
                f"• <b>Fourgreen (Корея):</b> 150 000 - 215 000 сум\n"
                f"• <b>Fourgreen Керамика:</b> 300 000 - 350 000 сум\n"
                f"• <b>Hardron (Премиум Керамика):</b> 350 000 - 365 000 сум\n"
                f"• <b>Japanparts:</b> 170 000 сум\n"
                f"• <b>Brake Master:</b> 150 000 - 170 000 сум\n"
                f"• <b>GM Original:</b> 750 000 сум\n\n"
                f"🛠 <i>В сервисах Carland действует качественная замена и установка!</i>\n"
                f"📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )
        elif lang == "en":
            return (
                f"🛑 <b>Brake Pads for {car_title} in Stock:</b>\n\n"
                f"• <b>Fourgreen (Korea):</b> 150,000 - 215,000 UZS\n"
                f"• <b>Fourgreen Ceramic:</b> 300,000 - 350,000 UZS\n"
                f"• <b>Hardron (Premium Ceramic):</b> 350,000 - 365,000 UZS\n"
                f"• <b>Japanparts:</b> 170,000 UZS\n"
                f"• <b>Brake Master:</b> 150,000 - 170,000 UZS\n"
                f"• <b>GM Original:</b> 750,000 UZS\n\n"
                f"🛠 <i>Professional installation available at Carland branches!</i>\n"
                f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )
        return (
            f"🛑 <b>{car_title} uchun tormoz kolodkalari narxlari:</b>\n\n"
            f"• <b>Fourgreen (Koreya):</b> 150 000 - 215 000 so'm\n"
            f"• <b>Fourgreen Keramika:</b> 300 000 - 350 000 so'm\n"
            f"• <b>Hardron (Premium Keramika):</b> 350 000 - 365 000 so'm\n"
            f"• <b>Japanparts:</b> 170 000 so'm\n"
            f"• <b>Brake Master:</b> 150 000 - 170 000 so'm\n"
            f"• <b>GM Original:</b> 750 000 so'm\n\n"
            f"🛠 <i>Carland filiallarida o'rnatib berish xizmati mavjud!</i>\n"
            f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
        )

    # 3. SVECHALAR (masalan: "Kobalt svecha", "Tracker svecha", "Gentra svecha")
    if any(w in q_lower for w in ["svecha", "svechalar", "свечи", "свеча", "spark", "plug"]):
        car_code = detect_car_code(q_norm)
        if car_code in ["tracker", "onix"]:
            if lang == "ru":
                return (
                    f"⚡️ <b>Свечи зажигания для Tracker 2 / Onix:</b>\n\n"
                    f"• <b>ACDelco GM Original 12706611:</b> комплект из 3 шт. 350 000 сум + замена 60 000 = <b>410 000 сум</b>\n\n"
                    f"🛠 <i>Оригинальные свечи и профессиональная установка в Carland!</i>\n"
                    f"📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
                )
            elif lang == "en":
                return (
                    f"⚡️ <b>Spark Plugs for Tracker 2 / Onix:</b>\n\n"
                    f"• <b>ACDelco GM Original 12706611:</b> set of 3 pcs 350,000 UZS + service 60,000 = <b>410,000 UZS</b>\n\n"
                    f"🛠 <i>Original spark plugs and guaranteed installation at Carland!</i>\n"
                    f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
                )
            return (
                f"⚡️ <b>Tracker 2 / Onix uchun svechalar narxi:</b>\n\n"
                f"• <b>ACDelco GM Original 12706611:</b> 3 dona komplekt 350 000 so'm + xizmat 60 000 = <b>410 000 so'm</b>\n\n"
                f"🛠 <i>Carland servislarida original svechalar mavjud!</i>\n"
                f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )
        else:
            car_label = car_code.capitalize() if car_code else "Cobalt / Gentra / Nexia 3"
            if lang == "ru":
                return (
                    f"⚡️ <b>Свечи зажигания для {car_label} и стоимость замены:</b>\n\n"
                    f"• <b>ACDelco GM Original:</b> 4 шт. 160 000 сум + замена 70 000 = <b>230 000 сум</b>\n"
                    f"• <b>Autozip (Корея):</b> 4 шт. 130 000 сум + замена 70 000 = <b>200 000 сум</b>\n\n"
                    f"🛠 <i>Гарантия и профессиональная замена в автосервисах Carland!</i>\n"
                    f"📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
                )
            elif lang == "en":
                return (
                    f"⚡️ <b>Spark Plugs and Installation for {car_label}:</b>\n\n"
                    f"• <b>ACDelco GM Original:</b> 4 pcs 160,000 UZS + service 70,000 = <b>230,000 UZS</b>\n"
                    f"• <b>Autozip (Korea):</b> 4 pcs 130,000 UZS + service 70,000 = <b>200,000 UZS</b>\n\n"
                    f"🛠 <i>Professional installation and warranty at Carland!</i>\n"
                    f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
                )
            return (
                f"⚡️ <b>{car_label} uchun svechalar va almashtirish narxi:</b>\n\n"
                f"• <b>ACDelco GM Original:</b> 4 dona 160 000 so'm + xizmat 70 000 = <b>230 000 so'm</b>\n"
                f"• <b>Autozip (Koreya):</b> 4 dona 130 000 so'm + xizmat 70 000 = <b>200 000 so'm</b>\n\n"
                f"🛠 <i>Carland ustalaridan sifatli o'rnatish va kafolat!</i>\n"
                f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )

    # 4. AKKUMULYATOR (masalan: "Kobalt akkumulyator", "Gentra akkum", "Damas akkum")
    if any(w in q_lower for w in ["akkum", "akkumulyator", "аккумулятор", "battery", "starter cmf", "delkor"]):
        if lang == "ru":
            return (
                f"🔋 <b>Качественные аккумуляторы в сети Carland:</b>\n\n"
                f"• <b>STARTER CMF 60AR 60Ah:</b> 855 000 сум (идеально для Cobalt, Gentra, Lacetti, Nexia 3);\n"
                f"• В наличии Delkor, Bars и аккумуляторы для любых марок авто;\n"
                f"• 🛠 <b>Бесплатная диагностика генератора и установка</b> в наших филиалах!\n\n"
                f"📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )
        elif lang == "en":
            return (
                f"🔋 <b>Car Batteries at Carland:</b>\n\n"
                f"• <b>STARTER CMF 60AR 60Ah:</b> 855,000 UZS (ideal for Cobalt, Gentra, Lacetti, Nexia 3);\n"
                f"• Delkor, Bars, and batteries for all car makes in stock;\n"
                f"• 🛠 <b>Free diagnostics and battery installation</b> at all branches!\n\n"
                f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )
        return (
            f"🔋 <b>Carland do'konlarida sifatli akkumulyatorlar:</b>\n\n"
            f"• <b>STARTER CMF 60AR 60Ah:</b> 855 000 so'm (Cobalt, Gentra, Lacetti, Nexia 3 uchun ideal);\n"
            f"• Shuningdek, Delkor, Bars va boshqa barcha modellar uchun akkumulyatorlar bor;\n"
            f"• 🛠 Filiallarimizda <b>bepul diagnostika va o'rnatib berish</b> xizmati mavjud!\n\n"
            f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
        )

    # 5. PAMPERS / BENZANASOS FILTRI
    if any(w in q_lower for w in ["pampers", "памперс"]):
        if lang == "ru":
            return (
                "⛽️ <b>Сетка-фильтр бензонасоса (Памперс):</b>\n\n"
                "• 'Памперс' — это очищающий сетчатый фильтр, установленный на бензонасосе в топливном баке;\n"
                "• В филиалах Carland проводится промывка топливного бака, диагностика насоса и замена фильтра-памперса на новый!\n\n"
                "📞 Call-центр: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )
        elif lang == "en":
            return (
                "⛽️ <b>Fuel Pump Strainer Filter (Pampers):</b>\n\n"
                "• 'Pampers' is the fuel strainer mesh filter inside the fuel tank on the fuel pump;\n"
                "• Carland provides fuel tank cleaning, pump diagnostics, and strainer replacement!\n\n"
                "📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
            )
        return (
            "⛽️ <b>Yoqilg'i baki pampers (setka) filtri:</b>\n\n"
            "• 'Pampers' — bu yonilg'i baki ichidagi benzanasosga o'rnatilgan tozalovchi setkali filtr;\n"
            "• Carland filiallarida benzobakni yuvish, benzanasos diagnostikasi va pampers filtrini yangisiga almashtirish xizmati mavjud!\n\n"
            "📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a> | /filiallar"
        )

    # 6. MOY QOVUSHQOQLIGI BILAN QISQA SO'ROV (masalan: "Kobalt 5w30", "Cobalt 0w20", "Gentra 5w40")
    has_viscosity = re.search(r'\b(0w20|5w30|5w40|10w40|75w90|atf6)\b', q_lower.replace("-", ""))
    car_code = detect_car_code(q_norm)
    if has_viscosity and car_code:
        visc = has_viscosity.group(1).upper()
        tech = CAR_TECHNICAL_SPECS.get(car_code, {
            "car_name": car_code.capitalize(),
            "engine_oil": "3.5 - 4.0 litr",
            "viscosity": visc
        })
        car_name = tech["car_name"]
        oil_vol = tech["engine_oil"]

        if lang == "ru":
            return (
                f"🛢 <b>Моторное масло {visc} для {car_name}:</b>\n\n"
                f"• Объем заливки в двигатель: <b>{oil_vol}</b> ({tech['viscosity']});\n"
                f"• 🏷 <b>Ассортимент и цены:</b> Shell, Castrol, Liqui Moly, Valvoline, Total, Champion;\n"
                f"• 🛠 <b>ВАЖНОЕ ПРАВИЛО:</b> При покупке моторного масла в Carland, <b>замена масла БЕСПЛАТНАЯ!</b>\n\n"
                f"📞 Точный расчет и консультация: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"📍 Адреса филиалов: /filiallar"
            )
        elif lang == "en":
            return (
                f"🛢 <b>{visc} Engine Oil for {car_name}:</b>\n\n"
                f"• Engine oil capacity: <b>{oil_vol}</b> ({tech['viscosity']});\n"
                f"• 🏷 <b>Brands available:</b> Shell, Castrol, Liqui Moly, Valvoline, Total, Champion;\n"
                f"• 🛠 <b>IMPORTANT RULE:</b> When buying engine oil at Carland, <b>replacement service is completely FREE!</b>\n\n"
                f"📞 Consultation and booking: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"📍 Nearest branch: /filiallar"
            )
        return (
            f"🛢 <b>{car_name} uchun {visc} mator moyi:</b>\n\n"
            f"• Dvigatel moyi hajmi: <b>{oil_vol}</b> ({tech['viscosity']});\n"
            f"• 🏷 <b>Mavjud brendlar:</b> Shell, Castrol, Liqui Moly, Valvoline, Total, Champion;\n"
            f"• 🛠 <b>MUHIM QOIDA:</b> Carland servislarida mator moyi xarid qilinganda, <b>almashtirish MUTLAQO BEPUL!</b>\n\n"
            f"📞 Narxini hisoblash va navbatga yozilish: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            f"📍 O'zingizga yaqin filial: /filiallar"
        )

    # 7. KAROBKA / REDUKTOR MOYI (masalan: "Kobalt karobka", "Cobalt atf", "Gentra avtomat", "Aion reduktor")
    is_gear_query = any(w in q_lower for w in ["karobka", "akpp", "atf", "reduktor", "mexanika", "mkpp", "коробка", "кпп", "редуктор", "gearbox", "transmission"])
    if is_gear_query and car_code:
        tech = CAR_TECHNICAL_SPECS.get(car_code, {
            "car_name": car_code.capitalize(),
            "atf": "7 litr ATF6",
            "manual": "2.5 litr 75w90"
        })
        car_name = tech["car_name"]
        atf_info = tech["atf"]
        manual_info = tech["manual"]

        if lang == "ru":
            return (
                f"⚙️ <b>Масло коробки передач / редуктора для {car_name}:</b>\n\n"
                f"• ⚡️ <b>Автомат (АКПП / Редуктор):</b> {atf_info}\n"
                + (f"• 🕹 <b>Механика (МКПП):</b> {manual_info}\n" if manual_info != "-" else "") +
                f"\n🛠 <b>ВАЖНО:</b> Замена масла в коробке передач и редукторе — платная услуга (стоимость зависит от марки авто);\n"
                f"💡 <i>Акция: Полная аппаратная замена масла в АКПП со спец. промывкой — 720 000 сум!</i>\n\n"
                f"📞 Консультация Call-центра: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"📍 Филиалы: /filiallar"
            )
        elif lang == "en":
            return (
                f"⚙️ <b>Transmission / Reductor Oil for {car_name}:</b>\n\n"
                f"• ⚡️ <b>Automatic (AT / Reductor):</b> {atf_info}\n"
                + (f"• 🕹 <b>Manual (MT):</b> {manual_info}\n" if manual_info != "-" else "") +
                f"\n🛠 <b>IMPORTANT:</b> Gearbox and differential oil replacement requires a vehicle-specific service fee;\n"
                f"💡 <i>Promo: Full automatic transmission apparatus flush and replacement — 720,000 UZS!</i>\n\n"
                f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
                f"📍 Branches: /filiallar"
            )
        return (
            f"⚙️ <b>{car_name} uzatmalar qutisi (Karobka) / Reduktor moyi:</b>\n\n"
            f"• ⚡️ <b>Avtomat (AKPP / Reduktor):</b> {atf_info}\n"
            + (f"• 🕹 <b>Mexanika (MKPP):</b> {manual_info}\n" if manual_info != "-" else "") +
            f"\n🛠 <b>MUHIM:</b> Karobka va reduktor moyini almashtirishda mashina rusumiga qarab xizmat haqi olinadi;\n"
            f"💡 <i>Aksiya: Avtomat karobka moyini maxsus apparatda to'liq yuvish va almashtirish — 720 000 so'm!</i>\n\n"
            f"📞 Call-center: <a href=\"tel:+998555161616\">+998 55 516 16 16</a>\n"
            f"📍 O'zingizga yaqin filial: /filiallar"
        )

    return None
