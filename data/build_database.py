"""
Carland uchun yakuniy SQLite bazasini yig'ish skripti.

Manba fayllar (shu papkada, PDF/XLSX dan oldindan chiqarilgan xom JSON):
  - oil_table_raw.json        -> mashina rusumi bo'yicha motor/karobka/reduktor moy hajmi va turi
  - tires_raw.json            -> mashina rusumi bo'yicha shina o'lchamlari
  - batteries_raw.json        -> akkumulyator narxlari va mos mashinalar
  - antifreeze_raw.json       -> antifriz narxlari
  - svecha_raw.json           -> svecha (GM) narxlari
  - products_catalog_raw.json -> umumiy mahsulotlar katalogi (filtrlar, moylar, ehtiyot qismlar...)
  - promotions_sentabr.json   -> aksiya (kampaniya) paketlari
  - branches_structured.json  -> filiallar manzillari

Natija: carland.db (SQLite) — bot shu faylni o'qib ishlaydi.

Qayta ishlatish: manba fayllar yangilansa, shunchaki:
    python3 build_database.py
"""
import json
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).parent
DB_PATH = BASE / "carland.db"


def load(name):
    with open(BASE / name, encoding="utf-8") as f:
        return json.load(f)


def parse_float(s):
    """'3,5 litr' -> 3.5 ; '6 - 6,5 litr CVT' -> 6.5 ; '' -> None"""
    if not s:
        return None
    s = s.replace(",", ".")
    nums = re.findall(r"\d+\.?\d*", s)
    if not nums:
        return None
    return float(nums[-1])  # oxirgi (yuqori chegara) qiymatni olamiz


# Ba'zi qatorlarda hajm va moy turi bitta katakchada aralash yozilgan
# ('9 L ATF-8', '2 L 75W-85') — bunday holda oddiy parse_float moy turidagi
# raqamni (masalan "ATF-8" dagi 8 ni) litr hajmi deb noto'g'ri o'qib
# qolishi mumkin. Shu sababli litr sonini olishdan oldin moy turi
# belgilarini matndan tozalab tashlaymiz.
_CLEAN_TYPE_RE = re.compile(
    r"ATF[-\s]?\d*|(?:DEXRON|DX)[-\s]?(?:VI|III|II|\d+)|\d{1,2}\s*W\s*-?\s*\d{2,3}"
    r"|CVT|DCT|DSG|CASTROL[-\s]?D\s?X?\d*",
    re.IGNORECASE,
)


def parse_volume_liters(s):
    """Hajm katakchasidan moy turi belgilarini olib tashlab, faqat litr
    sonini o'qiydi (masalan '9 L ATF-8' -> 9.0, '6 - 7 litr ATF6' -> 7.0)."""
    return parse_float(_CLEAN_TYPE_RE.sub(" ", s or ""))


def parse_km(s):
    """'25 000' -> 25000 ; probel minglik ajratkich sifatida ishlatiladi, vergul emas."""
    if not s:
        return None
    digits = re.sub(r"[^\d]", "", str(s))
    return int(digits) if digits else None


def parse_int_price(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return int(s)
    s = str(s).replace("​", "").strip()
    s = re.sub(r"[.,]\d{2}\s*$", "", s)  # oxiridagi ,00 ni olib tashlaymiz
    s = re.sub(r"[^\d]", "", s)
    return int(s) if s else None


# Muhim: alternativalar tartibi ahamiyatli — "ATF ESP4" kabi qo'shma nom
# oddiy "ATF"dan OLDIN tekshirilishi kerak, aks holda "ESP4" qismi yo'qolib
# ketadi. Manba jadvalda ba'zi katakchalarda bir nechta pozitsiya vergulsiz,
# faqat probel bilan (yoki hech qanday ajratkichsiz) yozilgan — masalan
# "75w90 ATF6" yoki "ATF6CVT" — shuning uchun vergul bo'yicha split emas,
# har bir haqiqiy pozitsiyani alohida qidiradigan (findall) yondashuv kerak.
VISCOSITY_RE = re.compile(
    r"\d{1,2}\s*W\s*-?\s*\d{2,3}"   # 5W30, 75W90, 5W-30
    r"|ATF\s*ESP\s*\d*"             # ATF ESP4
    # ATF + bitta raqam (2/3/6 — haqiqiy Dexron avlodlari), lekin FAQAT undan
    # keyin so'z chegarasi bo'lsa — "ATF 6400" yoki "ATF 9600" kabi mahsulot
    # kodlarini "ATF6"/"ATF9" deb noto'g'ri o'qib qolmaslik uchun (bunday
    # holda \b sinovi muvaffaqiyatsiz bo'lib, faqat "ATF" o'zi qaytariladi).
    r"|ATF\s*[2368]?\b"
    r"|\bCVT\b|\bDCT\b|\bDSG\b|\bEV\b",
    re.IGNORECASE,
)


def norm_viscosity(s):
    if not s:
        return None
    return re.sub(r"\s+", "", s.upper().replace("-", ""))


def parse_oil_types(raw):
    """'75w90 ATF6' -> ['75W90','ATF6'] ; 'ATF6CVT' -> ['ATF6','CVT']
    Vergul/space/ajratkichsiz yozilgan pozitsiyalarni ham to'g'ri ajratadi."""
    if not raw or "praklatka" in raw.lower():  # manbadagi tasodifiy izoh, moy turi emas
        return []
    out = [norm_viscosity(m) for m in VISCOSITY_RE.findall(raw)]
    out = [v for v in out if v]
    # "Castrol-D2"/"Castrol D1"/"Castrol W5" — bular Castrol ON EV
    # seriyasining elektromobil/gibrid reduktorlari uchun moylari; bazadagi
    # mos mahsulotlar "EV" deb belgilangan, shunga moslashtiramiz.
    if re.search(r"castrol[-\s]?(d[12]|w5)\b", raw, re.IGNORECASE) and "EV" not in out:
        out.append("EV")
    return list(dict.fromkeys(out))  # dublikatlarsiz, tartib saqlanadi



# Manba PDF'da ko'p zamonaviy (asosan xitoy va yangi GM/Chevrolet) modellar
# uchun motor moyi VISKOZITETI umuman ko'rsatilmagan (faqat hajm bor) — bunday
# 28 taga yaqin model uchun "Motor moyi narxlari" bo'limi hech narsa
# topolmay bo'sh chiqib qolardi. Shu sabab, motor OYLI (litri) bor, lekin
# turi noma'lum modellar uchun, model nomidan kelib chiqib, shu marka/avlod
# uchun odatiy tavsiya etiladigan viskozitetlarni taxminan belgilaymiz —
# aniq raqam OEM qo'llanmasida tekshirilishi kerak, lekin mijozga hech
# qanday variant ko'rsatmasdan qolishdan ko'ra ancha foydali.
_ENGINE_OIL_FALLBACK_RULES = [
    (("GENTRA", "LACETTI"), ["5W30", "5W40", "10W40"]),
    (("EQUINOX", "TRAVERSE", "TAHOE"), ["0W20", "5W30"]),
    (("CADDY",), ["5W30"]),
    (("BESTUNE", "DONGFENG AEOLUS", "HAVAL", "JETOUR", "MONZA",
      "CHERY ARRIZO", "CHERY TIGGO", "LADA VESTA"), ["5W30", "5W40"]),
    (("BYD HAN", "BYD SONG", "BYD YUAN UP", "AITO", "VOYAH FREE"), ["0W20", "5W30"]),
    (("KIA K8", "KIA SONET", "HYUNDAI TUCSON", "HYUNDAI ELANTRA", "HYUNDAI CRETA"), ["0W20", "5W30"]),
]


def default_engine_oil_types(model_name: str) -> list:
    up = model_name.upper()
    for keywords, types in _ENGINE_OIL_FALLBACK_RULES:
        if any(k in up for k in keywords):
            return types
    return []


def detect_gearbox_kind(raw, oil_type_raw=None):
    """Ko'p Kia/Hyundai qatorlarida hajm katakchasida ('6 - 7 litr ATF6' kabi)
    turi so'zi bilan aytilmagan, faqat moy turi orqali bilinadi ('CVT', 'ATF...').
    Shu sabab, agar hajm matnida aniq kalit so'z topilmasa, moy turidan xulosa
    chiqaramiz (CVT -> Variator, ATF... -> Avtomat, faqat gear-moy -> Mexanika)."""
    low = (raw or "").lower()
    if "dct" in low or "dsg" in low:
        return "Robotlashtirilgan qutisi (DCT/DSG)"
    if "mexanika" in low or "mkpp" in low:
        return "Mexanika (MKPP)"
    if "avtomat" in low or "akpp" in low:
        return "Avtomat (AKPP)"
    if "cvt" in low:
        return "Variator (CVT)"
    if " ev" in low or low.strip() == "ev":
        return "Elektromotor reduktori"

    ot = (oil_type_raw or "").lower()
    if "cvt" in ot:
        return "Variator (CVT)"
    if "dct" in ot or "dsg" in ot:
        return "Robotlashtirilgan qutisi (DCT/DSG)"
    if "atf" in ot:
        return "Avtomat (AKPP)"
    if re.search(r"\d{1,2}w-?\d{2,3}", ot):  # faqat 75w90 kabi gear-moy -> mexanika
        return "Mexanika (MKPP)"
    return None


ENGINE_VARIANT_RE = re.compile(
    r"(\d[\d.,]*)\s*(?:motorli|matorli|=)\s*-?\s*(\d[\d.,]*)\s*(?:/\s*(\d[\d.,]*))?\s*litr",
    re.IGNORECASE,
)


GEARBOX_MANUAL_RE = re.compile(r"(?:MKPP|MEXANIKA)\s*([\d.,]+)\s*litr\s*(\d{1,2}w-?\d{2,3})", re.IGNORECASE)
GEARBOX_AUTO_RE = re.compile(r"([\d.,]+)\s*litr\s*(ATF\s*\d*)", re.IGNORECASE)


def split_gearbox_variants(volume_raw, type_raw):
    """Ba'zi qatorlarda (Nexia 3, Gentra) bitta katakchada HAM mexanika,
    HAM avtomat variantlari birga yozilgan ('MKPP 2 litr 75w-90. AKPP 7 litr
    ATF6.'). Bunday holda ikkita alohida variantga ajratamiz — aks holda
    ikkalasi bitta noto'g'ri qiymatga aralashib qolar edi.
    Qaytaradi: [(kind, liters, oil_types_raw), ...] yoki ajratish shart
    bo'lmasa None."""
    m_manual = GEARBOX_MANUAL_RE.search(volume_raw or "")
    m_auto = GEARBOX_AUTO_RE.search(volume_raw or "")
    if not (m_manual and m_auto):
        return None
    return [
        ("Mexanika (MKPP)", parse_float(m_manual.group(1)), m_manual.group(2)),
        ("Avtomat (AKPP)", parse_float(m_auto.group(1)), m_auto.group(2)),
    ]


def split_engine_variants(raw):
    """Bitta katakchada bir nechta dvigatel hajmi/moy hajmi kombinatsiyasi bo'lsa
    ('2 motorli-4,5 litr 2,5 motorli-6 litr' kabi), ularni alohida variantlarga ajratadi.
    Qaytaradi: [(dvigatel_hajmi_str, moy_litr_float), ...] yoki bitta variant bo'lsa ham shu shaklda.
    """
    matches = ENGINE_VARIANT_RE.findall(raw or "")
    if len(matches) < 2:
        return None  # variant ajratish shart emas, umumiy parser ishlatiladi
    out = []
    for engine_size, litr1, litr2 in matches:
        candidates = [parse_float(litr1)]
        if litr2:
            candidates.append(parse_float(litr2))
        volume = max(c for c in candidates if c is not None)
        out.append((engine_size.replace(",", "."), volume))
    return out


# Ko'p ATF mahsulotlari "ATF6" deb emas, "DEXRON VI", "ATF DX 6", "ATF VI"
# kabi yozilgan — bular AYNAN ATF6 bilan bir xil avlod. Buni to'g'ri
# aniqlamasak, ATF3 (eski) va ATF6 (yangi) mahsulotlari bir-biriga
# aralashib, mos kelmaydigan moy tavsiya qilinishi mumkin — shu sabab
# alohida, ATF/DEXRON avlod raqamlarini aniq o'qiydigan tekshiruv kerak.
_ROMAN_GEN = {"VI": "6", "III": "3", "II": "2"}
ATF_GEN_RE = re.compile(
    r"DEXRON\s*-?\s*(VI|III|II|\d)"       # DEXRON VI / DEXRON 6
    r"|\bDX\s*-?\s*(VI|III|II|\d)\b"      # DX-6, DX 3
    r"|\bATF\s*-?\s*(VI|III|II)\b",       # ATF VI, ATF-III
    re.IGNORECASE,
)
CVT_DCT_RE = re.compile(r"\bCVT\b|\bDCT\b|\bDSG\b", re.IGNORECASE)


def find_viscosity_in_name(name, category=None):
    """category='Motor oils' bo'lsa ATF/DEXRON qidiruvi o'tkazilmaydi — chunki
    dvigatel moylarida "DX1"/"DX2" GM DEXOS1/DEXOS2 standartini bildiradi,
    Dexron (avtomat uzatmalar moyi) bilan hech qanday aloqasi yo'q. Buni
    ajratmasak, masalan "LIQUI MOLY ... DX1 5W30" nomli dvigatel moyi
    xato ravishda "ATF1" deb belgilanib, o'zining haqiqiy 5W30 ko'rsatkichi
    yo'qolib qolar edi."""
    upper = name.upper()

    if category != "Motor oils":
        m = ATF_GEN_RE.search(upper)
        if m:
            gen = m.group(1) or m.group(2) or m.group(3)
            gen = _ROMAN_GEN.get(gen.upper(), gen)
            return f"ATF{gen}"

        m = CVT_DCT_RE.search(upper)
        if m:
            return m.group(0).upper()

    m = VISCOSITY_RE.search(upper)
    return norm_viscosity(m.group(0)) if m else None


def parse_pack_size(name):
    """'GRAUMANN 10W40 ECONOMY 4/1 L' -> idish hajmi haqida matn, masalan '4L yoki 1L idish'."""
    m = re.search(r"(\d+)\s*/\s*1\s*L", name, re.IGNORECASE)
    if m:
        return f"{m.group(1)}L / 1L idish"
    m = re.search(r"\b(\d+)\s*L\b", name, re.IGNORECASE)
    if m:
        return f"{m.group(1)}L idish"
    m = re.search(r"(\d+)\s*л", name, re.IGNORECASE)
    if m:
        return f"{m.group(1)}L idish"
    return None


def build():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE cars (
            id INTEGER PRIMARY KEY,
            model TEXT NOT NULL,
            engine_oil_liters REAL,
            engine_oil_types TEXT,      -- JSON list
            gearbox_kind TEXT,
            gearbox_liters REAL,
            reductor_liters REAL,
            reductor_oil_types TEXT,    -- JSON list
            gearbox_oil_types TEXT,     -- JSON list
            change_interval_km INTEGER,
            raw_engine_volume TEXT,
            raw_gearbox_volume TEXT,
            raw_reductor_volume TEXT
        );

        CREATE TABLE tires (
            id INTEGER PRIMARY KEY,
            model TEXT NOT NULL,
            years TEXT,
            sizes TEXT   -- JSON list
        );

        CREATE TABLE batteries (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT,
            price INTEGER,
            cars TEXT   -- JSON list
        );

        CREATE TABLE antifreeze (
            id INTEGER PRIMARY KEY,
            brand TEXT,
            model TEXT NOT NULL,
            bachok_price INTEGER,
            liters REAL,
            service_price INTEGER,
            summa_qizil INTEGER,
            summa_kok INTEGER
        );

        CREATE TABLE spark_plugs (
            id INTEGER PRIMARY KEY,
            model TEXT NOT NULL,
            qty INTEGER,
            price INTEGER
        );

        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price INTEGER,
            viscosity TEXT,
            pack_size TEXT
        );

        CREATE TABLE promotions (
            id INTEGER PRIMARY KEY,
            package_title TEXT,
            model TEXT,
            oil_liters REAL,
            oil_price INTEGER,
            details TEXT   -- JSON of remaining columns
        );

        CREATE TABLE branches (
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
            address TEXT,
            directions TEXT
        );

        CREATE VIRTUAL TABLE products_fts USING fts5(name, category, content='products', content_rowid='id');
        """
    )

    # ---- cars ----
    for r in load("oil_table_raw.json"):
        variants = split_engine_variants(r["engine_oil_volume_raw"])
        if variants is None:
            variants = [(None, parse_float(r["engine_oil_volume_raw"]))]

        gearbox_variants = split_gearbox_variants(r["gearbox_volume_raw"], r["gearbox_oil_type_raw"])

        for engine_size, engine_liters in variants:
            base_model = r["model"] if engine_size is None else f'{r["model"]} {engine_size}L'

            # Ko'p Kia/Hyundai/GM qatorlarida moy turi (ATF6, 75W-85 va h.k.)
            # alohida "moy turi" katakchasida emas, balki hajm katakchasining
            # o'zida yozilgan ('6 - 7 litr ATF6'). Shu sabab ikkalasini
            # birlashtirib qidiramiz — aks holda bu turdagi ko'p mashinalar
            # uchun moy turi butunlay yo'qolib qolar edi.
            combined_type_raw = f"{r['gearbox_oil_type_raw'] or ''} {r['gearbox_volume_raw'] or ''}"
            gb_options = gearbox_variants or [(
                detect_gearbox_kind(r["gearbox_volume_raw"], combined_type_raw),
                parse_volume_liters(r["gearbox_volume_raw"]),
                combined_type_raw,
            )]

            for gb_kind, gb_liters, gb_type_raw in gb_options:
                model_name = base_model if len(gb_options) == 1 else f"{base_model} ({gb_kind.split()[0]})"
                cur.execute(
                    """INSERT INTO cars (model, engine_oil_liters, engine_oil_types, gearbox_kind,
                        gearbox_liters, reductor_liters, reductor_oil_types, gearbox_oil_types, change_interval_km,
                        raw_engine_volume, raw_gearbox_volume, raw_reductor_volume)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        model_name,
                        engine_liters,
                        json.dumps(
                            parse_oil_types(r["engine_oil_type_raw"])
                            or (default_engine_oil_types(model_name) if engine_liters else [])
                        ),
                        gb_kind,
                        gb_liters,
                        parse_volume_liters(r["reductor_volume_raw"]),
                        json.dumps(parse_oil_types(r["reductor_volume_raw"])),
                        json.dumps(parse_oil_types(gb_type_raw)),
                        parse_km(r["change_interval_km_raw"]),
                        r["engine_oil_volume_raw"],
                        r["gearbox_volume_raw"],
                        r["reductor_volume_raw"],
                    ),
                )

    # ---- tires ----
    for r in load("tires_raw.json"):
        cur.execute(
            "INSERT INTO tires (model, years, sizes) VALUES (?,?,?)",
            (r["model"], r["years"], json.dumps(r["sizes"], ensure_ascii=False)),
        )

    # ---- batteries (birinchi guruh sarlavha-chiqindi, o'tkazib yuboramiz) ----
    for r in load("batteries_raw.json"):
        if "Наименование" in " ".join(r.get("cars", [])) or r["battery"].startswith("Емкость"):
            continue
        cur.execute(
            "INSERT INTO batteries (name, brand, price, cars) VALUES (?,?,?,?)",
            (r["battery"], r["brand"], parse_int_price(r["price"]), json.dumps(r["cars"], ensure_ascii=False)),
        )

    # ---- antifreeze (uchta brend: VALESCO, FELIX, ZITRON - brand ustuni bilan ajratilgan) ----
    for r in load("antifreeze_raw.json"):
        cur.execute(
            """INSERT INTO antifreeze (brand, model, bachok_price, liters, service_price, summa_qizil, summa_kok)
               VALUES (?,?,?,?,?,?,?)""",
            (
                r["brand"], r["model"], parse_int_price(r["bachok_price"]), parse_float(r["liters"]),
                parse_int_price(r["service_price"]), parse_int_price(r["summa_qizil"]),
                parse_int_price(r["summa_kok"]) if r["summa_kok"] else None,
            ),
        )

    # ---- spark plugs: [model, '', '', qty, price, ''] ----
    for r in load("svecha_raw.json"):
        if len(r) < 5 or not r[0]:
            continue
        model = r[0]
        qty = r[3]
        price = r[4]
        cur.execute(
            "INSERT INTO spark_plugs (model, qty, price) VALUES (?,?,?)",
            (model, int(parse_float(qty) or 0) or None, parse_int_price(price)),
        )

    # ---- products catalog ----
    for r in load("products_catalog_raw.json"):
        name = r["name"]
        price = parse_int_price(r["price"])
        if price is None or price == 0:
            continue
        visc = find_viscosity_in_name(name, r["category"]) if r["category"] in ("Motor oils", "Transmission oils", "Transmission fluid") else None
        pack = parse_pack_size(name) if r["category"] in ("Motor oils", "Transmission oils", "Transmission fluid") else None
        cur.execute(
            "INSERT INTO products (name, category, price, viscosity, pack_size) VALUES (?,?,?,?,?)",
            (name, r["category"], price, visc, pack),
        )

    cur.execute("INSERT INTO products_fts (rowid, name, category) SELECT id, name, category FROM products")

    # ---- promotions ----
    promos = load("promotions_sentabr.json")
    for sheet, payload in promos.items():
        if sheet in ("AKKUMULATOR", "SVECHA GM"):
            continue  # boshqa jadvallarda alohida saqlanadi
        title = payload["title"]
        for row in payload["rows"]:
            model = row.get("AVTO")
            if not model:
                continue
            oil_liters = row.get("MOY")
            oil_price = row.get("MOY SUMMA")
            details = {k: v for k, v in row.items() if k not in ("AVTO", "MOY", "MOY SUMMA")}
            cur.execute(
                "INSERT INTO promotions (package_title, model, oil_liters, oil_price, details) VALUES (?,?,?,?,?)",
                (title, model, float(oil_liters) if isinstance(oil_liters, (int, float)) else parse_float(str(oil_liters)),
                 parse_int_price(oil_price), json.dumps(details, ensure_ascii=False, default=str)),
            )

    # ---- branches ----
    for b in load("branches_structured.json"):
        cur.execute(
            "INSERT INTO branches (id, name, city, address, directions) VALUES (?,?,?,?,?)",
            (b["id"], b["name"], b["city"], b["address"], b["directions"]),
        )

    conn.commit()

    # qisqacha statistika
    for t in ["cars", "tires", "batteries", "antifreeze", "spark_plugs", "products", "promotions", "branches"]:
        n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"{t}: {n} ta yozuv")

    conn.close()
    print(f"\nBaza tayyor: {DB_PATH}")


if __name__ == "__main__":
    build()
