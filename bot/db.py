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
# (masalan svecha va kolodka ro'yxatlari) ba'zi begona qatorlar "Motor
# oils"/"Transmission oils" kategoriyasiga yopishib qolgan. Moylar
# ro'yxatida bunday narsalar chiqmasligi uchun filtrlaymiz.
_NON_OIL_MARKERS = ("SVECHA", "СВЕЧА", "КОЛОДК", "KOLODKA", "NAME SALES PRICE", "ИМЯ")


def browse_oils_by_origin(categories: tuple[str, ...], origin: str, offset: int = 0, limit: int = 6):
    """origin: 'europe' yoki 'other'. Brend nomi european_brands ro'yxatida
    bo'lsa 'europe', aks holda 'other' toifasiga tushadi."""
    from . import config

    with get_conn() as conn:
        cat_ph = ",".join("?" * len(categories))
        all_rows = conn.execute(
            f"SELECT name, price FROM products WHERE category IN ({cat_ph}) ORDER BY name", categories
        ).fetchall()

    def brand_of(name: str) -> str:
        first = name.upper().split()[0] if name.split() else ""
        return first

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
        brand = brand_of(r["name"])
        is_euro = brand in config.EUROPEAN_OIL_BRANDS
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


# Bazada atigi 30 ta akkumulyator bor va ularning "cars" ro'yxati (manba
# PDF'dan) 94 mashinaning hammasini qamrab olmaydi. Shu sabab aniq moslik
# topilmasa ham (yoki topilgan bo'lsa-da qo'shimcha tanlov sifatida),
# mashina "klassi"ga (dvigatel hajmi, EV/gibrid yoki yo'qligi) qarab kerakli
# amper (Ah) ni TAXMINAN baholab, bazadagi eng yaqin amperli
# akkumulyator(lar)ni tavsiya qilamiz — bu ANIQ artikul mosligi emas, umumiy
# yo'riqnoma, xodim bilan tasdiqlash tavsiya etiladi.
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
