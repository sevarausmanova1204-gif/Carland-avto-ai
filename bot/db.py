"""SQLite ma'lumotlar bazasiga faqat-o'qish uchun kirish qatlami."""
import json
import re
import sqlite3
from contextlib import contextmanager

from .config import DB_PATH


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def list_cars():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, model FROM cars ORDER BY model").fetchall()
        return [dict(r) for r in rows]


def get_car(car_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["engine_oil_types"] = json.loads(d["engine_oil_types"] or "[]")
        d["gearbox_oil_types"] = json.loads(d["gearbox_oil_types"] or "[]")
        d["reductor_oil_types"] = json.loads(d["reductor_oil_types"] or "[]")
        return d


def search_cars(query: str, limit: int = 30):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, model FROM cars WHERE model LIKE ? ORDER BY model LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]


_NORMALIZE_RE = re.compile(r"[^\w'ʻʼ]+", re.UNICODE)
_APOSTROPHE_RE = re.compile(r"['ʻʼ’`]")


def _normalize(s: str) -> str:
    """Tinish belgilari/qavslar farqi tufayli aniq moslik o'tkazib
    yubormaslik uchun (masalan 'Captiva 2 va 3, 2.4L' vs bazadagi
    'Captiva 2 va 3 2.4L') matnni solishtirish oldidan soddalashtiradi."""
    return re.sub(r"\s+", " ", _NORMALIZE_RE.sub(" ", s.lower())).strip()


def normalize_word(w: str) -> str:
    """So'zni kichik harflarga o'tkazib, turli tutuq belgisi
    variantlarini ('\\'', 'ʻ', 'ʼ', '’') olib tashlaydi — shu bilan
    imlo farqidan qat'i nazar bir xil so'zlar bir xil ko'rinishga keladi."""
    return _APOSTROPHE_RE.sub("", w.lower())


# Umumiy avtomobil/moy/bot atamalari — bular ASLIDA mashina nomi EMAS,
# shu sabab erkin matnda mashina qidirishda (fallback bosqichida)
# e'tiborga olinmaydi. Aks holda, masalan, foydalanuvchi botning o'zi
# chiqargan "Avtomat (AKPP)" degan qatorni nusxalab yuborsa-yu, bazada
# faqat bitta model ("Gentra (Avtomat)") nomida "Avtomat" so'zi uchrasa,
# bot buni noto'g'ri ravishda "aynan shu mashina so'ralyapti" deb
# tushunib, butunlay boshqa (so'ralmagan) mashina uchun hisoblab
# qo'yishi mumkin edi — bu xato haqiqatda sodir bo'lgan.
GENERIC_WORD_STOPLIST = {
    "motor", "motorga", "matorga", "matoriga", "motoriga", "dvigatel", "dvigatelga",
    "moy", "moyi", "moyidan", "moylardan", "moylaridan", "moydan", "moylari",
    "karobka", "karobkaga", "karobkasiga", "korobka", "korobkaga", "korobkasiga",
    "transmissiya", "reduktor", "reduktorga", "reduktori",
    "avtomat", "avtomatik", "mexanika", "akpp", "mkpp",
    "hajmi", "hajm", "litr", "litri", "litrlik",
    "tavsiya", "etilgan", "tur", "turi", "turlari",
    "almashtirish", "oraligi", "vaqti",
    "hisobla", "hisoblab", "hisoblang", "hisoblansin", "hisoblashi",
    "yevropa", "evropa", "european", "osiyo", "xitoy", "koreys",
    "boshqa", "davlat", "davlatlar",
    "brend", "brenddan", "brendidan", "brendlaridan", "brendlardan", "brendi",
    "yaxshi", "eng", "arzon", "qimmat", "premium", "budjet", "budjetniy", "budjetli",
    "variant", "variantdagi", "variantlari",
    "ozing", "sizning", "uchun", "kerak", "qancha", "necha", "pul",
    "summa", "summasi", "qiymati", "narxi", "narxlari", "ber", "bering", "beradi",
}


def find_car_by_text(text: str):
    """Foydalanuvchi erkin matnida (shu jumladan botning o'zi chiqargan
    mashina kartochkasini nusxalab qo'shgan bo'lsa ham) ANIQ mos keladigan
    mashina modelini topishga harakat qiladi.

    Avval barcha mashina nomlari orasidan matn ichida to'liq uchraydigan ENG
    UZUN model nomini tanlaydi — bu, masalan, 'Captiva 2 va 3 2.4L' va
    'Captiva 2 va 3 3.0L' kabi o'xshash nomlar orasida chalkashmaslik uchun
    kerak (qisqa 'Captiva' so'zining o'zi bir nechta modelga to'g'ri kelib
    qolar edi). Aniq moslik topilmasa, matndagi (GENERIC_WORD_STOPLIST'dan
    tashqari) eng o'ziga xos (uzun) so'z bo'yicha bitta natijaga olib
    keladigan qidiruvga qaytadi — umumiy moy/karobka atamalari e'tiborga
    olinmaydi, chunki ular haqiqiy model nomi emas."""
    norm_text = _normalize(text)
    best = None
    best_len = 0
    for c in list_cars():
        norm_model = _normalize(c["model"])
        if norm_model and norm_model in norm_text and len(norm_model) > best_len:
            best = c
            best_len = len(norm_model)
    if best:
        return get_car(best["id"])

    words = sorted(
        {
            w for w in re.split(r"[^\w'ʻʼ]+", text, flags=re.UNICODE)
            if len(w) >= 3 and normalize_word(w) not in GENERIC_WORD_STOPLIST
        },
        key=len,
        reverse=True,
    )
    for w in words:
        matches = search_cars(w, limit=5)
        if len(matches) == 1:
            return get_car(matches[0]["id"])
    for w in words:
        matches = search_cars(w, limit=5)
        if matches:
            return get_car(matches[0]["id"])
    return None


_PACK_SUFFIX_RE = re.compile(r"\s*\(?\b\d+\s*/\s*1\s*L\)?\s*$|\s*\(?\b\d+\s*L\)?\s*$|\s*\(?\b\d+\s*л\)?\s*$", re.IGNORECASE)


def _base_name(name: str) -> str:
    """Idish hajmini ('4/1L', '5L' va h.k.) nomdan olib tashlab, mahsulotning
    'asosiy' nomini qaytaradi — bir xil moy turli idishda bir necha marta
    takrorlanib chiqmasligi uchun shu bo'yicha dublikatlar yig'ishtiriladi."""
    return re.sub(r"\s+", " ", _PACK_SUFFIX_RE.sub("", name)).strip().upper()


def get_oil_products(viscosities: list[str], category: str):
    """category: 'motor' yoki 'gearbox'. Bir xil moyning turli idish hajmidagi
    (4/1L, 5/1L va h.k.) yozuvlari bitta qatorga yig'ishtiriladi (eng arzoni
    saqlanadi), so'ng narx bo'yicha o'sish tartibida to'liq ro'yxat qaytariladi."""
    if not viscosities:
        return []
    with get_conn() as conn:
        placeholders = ",".join("?" * len(viscosities))
        if category == "gearbox":
            cats = ("Transmission oils", "Transmission fluid")
            cat_ph = ",".join("?" * len(cats))
            sql = (
                f"SELECT name, category, price, viscosity, pack_size FROM products "
                f"WHERE category IN ({cat_ph}) AND viscosity IN ({placeholders}) "
                f"ORDER BY price ASC"
            )
            params = (*cats, *viscosities)
        else:
            sql = (
                "SELECT name, category, price, viscosity, pack_size FROM products "
                f"WHERE category='Motor oils' AND viscosity IN ({placeholders}) "
                "ORDER BY price ASC"
            )
            params = (*viscosities,)
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]

    seen = {}
    deduped = []
    for r in rows:
        key = _base_name(r["name"])
        if key in seen:
            continue
        seen[key] = True
        deduped.append(r)
    return deduped


_ROMAN_TO_ARABIC = {
    "I": "1", "II": "2", "III": "3", "IV": "4", "V": "5",
    "VI": "6", "VII": "7", "VIII": "8", "IX": "9",
}
_ATF_SPEC_RE = re.compile(r"\bATF\s*-?\s*(\d+|[IVX]+)\b", re.IGNORECASE)


def _extract_atf_spec(text: str):
    """Matnda 'ATF' + raqam YOKI rim raqami (masalan 'ATF6', 'ATF 6',
    'ATF-6', 'ATF VI') ko'rinishidagi spetsifikatsiya bor-yo'qligini
    tekshiradi va uni bazadagi kanonik shaklga ('ATF6' kabi, bazaning
    `viscosity` ustunidagi format bilan bir xil) keltiradi. Shuningdek,
    shu spetsifikatsiya so'zi olib tashlangan "qoldiq" matnni (brend/nom
    qidiruvi uchun) qaytaradi. Mos kelmasa (None, asl matn) qaytaradi.

    Bu ayniqsa muhim, chunki bazadagi mahsulot NOMI ko'pincha spetsifikatsiyani
    boshqacha yozadi (masalan "KORELUX ATF DX 6" yoki "VALVOLINE ATF VI...")
    — shu sabab faqat nom matni bo'yicha izlash "Korelux Atf6" yoki "valvoline
    atf6" kabi so'rovlarni topa olmas edi. `viscosity` ustuni esa har doim
    aniq kanonik kod ("ATF6") bilan saqlangan, shu bilan solishtiramiz."""
    m = _ATF_SPEC_RE.search(text)
    if not m:
        return None, text
    raw = m.group(1).upper()
    num = raw if raw.isdigit() else _ROMAN_TO_ARABIC.get(raw)
    if num is None:
        return None, text
    remainder = text[:m.start()] + " " + text[m.end():]
    return f"ATF{num}", remainder


def search_oil_by_name(keyword: str, category: str, limit: int = 20):
    """Mijoz moy nomini (yoki brendini) yozganda, kategoriya bo'yicha
    (motor yoki karobka/reduktor) barcha moylar orasidan nomi mos
    kelganlarini qidiradi. Ikki usulda mos kelishni tekshiradi: (1) barcha
    so'zlar nomda (tartibsiz) uchraydimi — "Valvoline" kabi oddiy brend
    qidiruvi uchun; (2) so'rovda ATF spetsifikatsiyasi (masalan "Atf6"
    yoki "ATF VI") aniqlansa, uni bazaning `viscosity` ustuni bilan
    solishtiradi — bu nom matnida spetsifikatsiya boshqacha yozilgan
    (masalan "ATF DX 6") hollarda ham topib beradi."""
    spec, remainder = _extract_atf_spec(keyword)
    spec_words = [w for w in re.split(r"\s+", remainder.strip()) if len(w) >= 2]
    all_words = [w for w in re.split(r"\s+", keyword.strip()) if len(w) >= 2]

    with get_conn() as conn:
        if category == "gearbox":
            cats = ("Transmission oils", "Transmission fluid")
            cat_ph = ",".join("?" * len(cats))
            sql = f"SELECT name, category, price, viscosity, pack_size FROM products WHERE category IN ({cat_ph})"
            params = cats
        else:
            sql = "SELECT name, category, price, viscosity, pack_size FROM products WHERE category='Motor oils'"
            params = ()
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]

    matched = []
    for r in rows:
        name_up = r["name"].upper()
        name_word_match = bool(all_words) and all(w.upper() in name_up for w in all_words)
        spec_match = False
        if spec:
            visc = (r.get("viscosity") or "").upper().replace(" ", "").replace("-", "")
            if visc == spec:
                spec_match = not spec_words or all(w.upper() in name_up for w in spec_words)
        if name_word_match or spec_match:
            matched.append(r)
    matched.sort(key=lambda r: r["price"])

    seen = {}
    deduped = []
    for r in matched:
        key = _base_name(r["name"])
        if key in seen:
            continue
        seen[key] = True
        deduped.append(r)
        if len(deduped) >= limit:
            break
    return deduped


def _is_european_brand(name: str) -> bool:
    """Nomda taniqli Yevropa brendi mavjudligini so'z chegarasi bilan
    tekshiradi. Faqat nomning BIRINCHI so'ziga qarash yetarli emas: ba'zi
    yozuvlar brendni '...МОТОРНОЕ МАСЛО CASTROL...' yoki 'BREND CASTROL...'
    kabi o'rtada keltiradi, va 'LIQUI MOLY' kabi ikki so'zli brend nomi ham
    to'g'ri aniqlanishi kerak — shu sabab butun nom bo'ylab qidiramiz."""
    from . import config

    name_up = name.upper()
    for brand in config.EUROPEAN_OIL_BRANDS:
        if re.search(r"\b" + re.escape(brand) + r"\b", name_up):
            return True
    return False


def filter_oils_by_origin(products: list[dict], origin: str) -> list[dict]:
    """origin: 'europe' yoki 'other'. get_oil_products() natijasini (allaqachon
    narx bo'yicha saralangan) brend kelib chiqishi bo'yicha filtrlaydi —
    tartibni (narx o'sish tartibi) buzmaydi."""
    want_euro = origin == "europe"
    return [p for p in products if _is_european_brand(p["name"]) == want_euro]


def search_products_by_keyword(keyword: str, category: str, limit: int = 20):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT name, price FROM products WHERE category=? AND name LIKE ? ORDER BY price ASC LIMIT ?",
            (category, f"%{keyword}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]


def get_brake_pads_for_model(keyword: str, limit: int = 20):
    """Manba PDF'da ba'zi bo'lim sarlavhalari noto'g'ri formatda bo'lgani
    uchun tormoz kolodkalarining bir qismi "SPARE PART" ga, bir qismi esa
    xato ravishda "Transmission fluid" kategoriyasiga yozilib qolgan.
    Shu sabab kategoriyaga qaramay, BARCHA mahsulotlar orasidan nomi
    bo'yicha qidiramiz — bu qaysi kategoriyaga adashib yozilishidan
    qat'iy nazar to'g'ri ishlaydi."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT name, price FROM products WHERE name LIKE ? "
            "AND (UPPER(name) LIKE '%КОЛОДК%' OR UPPER(name) LIKE '%KOLODKA%' OR UPPER(name) LIKE '%BRAKE PAD%') "
            "ORDER BY price ASC LIMIT ?",
            (f"%{keyword}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]


# Manba PDF'da bir nechta bo'lim sarlavhasi noto'g'ri formatlangani sababli
# (masalan svecha va kolodka roYXatlari) ba'zi begona qatorlar "Motor
# oils"/"Transmission oils" kategoriyasiga yopishib qolgan. Moylar
# ro'yxatida bunday narsalar chiqmasligi uchun filtrlaymiz.
_NON_OIL_MARKERS = ("SVECHA", "СВЕЧА", "КОЛОДК", "KOLODKA", "NAME SALES PRICE", "ИМЯ")


def browse_oils_by_origin(categories: tuple[str, ...], origin: str, offset: int = 0, limit: int = 6):
    """origin: 'europe' yoki 'other'. Nomda european_brands ro'yxatidagi
    biror brend uchrasa 'europe', aks holda 'other' toifasiga tushadi."""
    with get_conn() as conn:
        cat_ph = ",".join("?" * len(categories))
        all_rows = conn.execute(
            f"SELECT name, price FROM products WHERE category IN ({cat_ph}) ORDER BY name", categories
        ).fetchall()

    filtered = []
    seen = set()
    for r in all_rows:
        name_up = r["name"].upper()
        if any(marker in name_up for marker in _NON_OIL_MARKERS) or len(r["name"]) > 120:
            continue
        key = (name_up, r["price"])
        if key in seen:
            continue
        seen.add(key)
        is_euro = _is_european_brand(r["name"])
        if (origin == "europe") == is_euro:
            filtered.append(dict(r))

    total = len(filtered)
    return filtered[offset:offset + limit], total


def browse_category(category: str, offset: int = 0, limit: int = 6):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT name, price FROM products WHERE category=? ORDER BY name LIMIT ? OFFSET ?",
            (category, limit, offset),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM (SELECT DISTINCT name, price FROM products WHERE category=?)", (category,)
        ).fetchone()[0]
        return [dict(r) for r in rows], total


def get_tires_for_model(keyword: str):
    """Mashina uchun mos shina o'lchamlarini, HAR BIR o'lcham uchun bazadagi
    narxlangan variantlar bilan birga qaytaradi (narxi/litr emas, dona narxi)."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT model, years, sizes FROM tires WHERE model LIKE ?", (f"%{keyword}%",)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            sizes = json.loads(d["sizes"])
            d["sizes"] = []
            for size in sizes:
                size_key = size.replace(" ", "").upper()
                priced = conn.execute(
                    "SELECT DISTINCT name, price FROM products WHERE category='Tires' AND REPLACE(UPPER(name),' ','') LIKE ? "
                    "ORDER BY price ASC LIMIT 6",
                    (f"{size_key}%",),
                ).fetchall()
                d["sizes"].append({"size": size, "options": [dict(p) for p in priced]})
            out.append(d)
        return out


# Bazada atigi 30 ta akkumulyator bor va ularning "cars" roYXati (manba
# PDF'dan) 94 mashinaning hammasini qamrab olmaydi. Shu sabab aniq moslik
# topilmasa ham (yoki topilgan bo'lsa-da qo'shimcha tanlov sifatida),
# mashina "klassi"ga (dvigatel hajmi, EV/gibrid yoki yo'qligi) qarab kerakli
# amper (Ah) ni TAXMINAN baholab, bazadagi eng yaqin amperli
# akkumulyator(lar)ni tavsiya qilamiz — bu ANIQ artikul mosligi emas, umumiy
# yo$riqnoma, xodim bilan tasdiqlash tavsiya etiladi.
_BATTERY_AH_OVERRIDES = {
    "STARTER 105D26 L": 90,
}

_TARGET_AH_RULES = [
    (("DAMAS", "LABO", "MATIZ", "TICO"), 40),
    (("NEXIA", "GENTRA", "LACETTI", "COBALT"), 45),
    (("MALIBU", "K5", "ELANTRA", "I 30", "MONZA", "BESTUNE", "ARRIZO", "AEOLUS"), 50),
    (("CRETA", "SELTOS", "SONET", "TIGGO 2", "TIGGO 4", "JOLION", "VESTA"), 45),
    (("SPORTAGE", "TUCSON", "SANTAFE", "SANTA FE", "SORENTO", "K8", "CAPTIVA",
      "EQUINOX", "H6", "M6", "DASHING", "X90", "TIGGO 7", "TIGGO 8", "TIGGO 9",
      "KODIAK"), 60),
    (("TRAVERSE", "TAHOE"), 80),
    (("CADDY",), 55),
    (("BYD", "VOYAH", "ZEEKR", "LEAPMOTOR", "AITO", "DONGFENG", "GAC AION", "HONGQI"), 50),
]


def _parse_battery_ah(name: str):
    if name in _BATTERY_AH_OVERRIDES:
        return _BATTERY_AH_OVERRIDES[name]
    m = re.search(r"(\d{2,3})\s*ah", name, re.IGNORECASE)
    return int(m.group(1)) if m else None


def _estimate_target_ah(model: str, engine_liters=None) -> int:
    up = model.upper()
    for keywords, ah in _TARGET_AH_RULES:
        if any(k in up for k in keywords):
            return ah
    if engine_liters:
        if engine_liters < 3:
            return 40
        if engine_liters < 4.5:
            return 45
        if engine_liters < 6:
            return 60
        return 74
    return 50


def get_batteries_for_model(model: str, keyword: str, engine_liters=None):
    """{"exact": [...], "estimated": [...], "target_ah": int} qaytaradi.
    "exact" — manba jadvalida shu model to'g'ridan-to'g'ri ko'rsatilgan
    akkumulyatorlar. "estimated" — aniq moslik topilmagan hollar uchun,
    taxmin qilingan amperga eng yaqin variantlar (aniq moslikda ko'rsatilgan
    nomlar takrorlanmaydi)."""
    with get_conn() as conn:
        rows = conn.execute("SELECT name, brand, price, cars FROM batteries").fetchall()

    all_batteries = []
    exact = []
    for r in rows:
        cars = json.loads(r["cars"])
        d = dict(r)
        d["cars"] = cars
        d["ah"] = _parse_battery_ah(r["name"])
        all_batteries.append(d)
        if any(keyword.upper() in c.upper() for c in cars):
            exact.append(d)

    exact_names = {b["name"] for b in exact}
    target_ah = _estimate_target_ah(model, engine_liters)
    with_ah = [b for b in all_batteries if b["ah"] is not None and b["name"] not in exact_names]
    with_ah.sort(key=lambda b: (abs(b["ah"] - target_ah), b["price"]))
    estimated = with_ah[:3]

    return {"exact": exact, "estimated": estimated, "target_ah": target_ah}


def get_antifreeze_for_model(keyword: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT brand, model, liters, summa_qizil, summa_kok FROM antifreeze WHERE model LIKE ?",
            (f"%{keyword}%",),
        ).fetchall()
        return [dict(r) for r in rows]


def get_spark_plug_for_model(keyword: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT model, qty, price FROM spark_plugs WHERE model LIKE ?", (f"%{keyword}%",)
        ).fetchall()
        return [dict(r) for r in rows]


def get_spark_plug_products_for_model(keyword: str, limit: int = 20):
    """GM (spark_plugs jadvali) dan tashqari, boshqa markalar (Kia, Hyundai,
    Skoda va h.k.) uchun svecha narxlari umumiy mahsulotlar katalogida,
    "Transmission oils" kategoriyasiga xato yozilib qolgan holda mavjud.
    Kategoriyaga qaramay, nomi bo'yicha qidiramiz."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT name, price FROM products WHERE name LIKE ? "
            "AND (UPPER(name) LIKE '%SVECHA%' OR UPPER(name) LIKE '%СВЕЧА%') "
            "ORDER BY price ASC LIMIT ?",
            (f"%{keyword}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]


def get_promotions_for_model(keyword: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT package_title, model, oil_liters, oil_price, details FROM promotions WHERE model LIKE ?",
            (f"%{keyword}%",),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["details"] = json.loads(d["details"])
            out.append(d)
        return out


def list_branches():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, city FROM branches ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def get_branch(branch_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM branches WHERE id=?", (branch_id,)).fetchone()
        return dict(row) if row else None


def fts_search_products(query: str, limit: int = 10):
    with get_conn() as conn:
        try:
            rows = conn.execute(
                "SELECT p.name, p.category, p.price FROM products_fts f "
                "JOIN products p ON p.id = f.rowid "
                "WHERE products_fts MATCH ? LIMIT ?",
                (query, limit),
            ).fetchall()
            return [dict(r) for r in rows]
        except sqlite3.OperationalError:
            return []
