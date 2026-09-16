"""
1-QADAM: manba PDF/XLSX fayllardan xom (raw) JSON fayllarni chiqarib olish.

Kirish:  data/raw/Carland umumiy ma'lumotlar-3.pdf
         data/raw/Aksiya SENTABR CALL SENTR.xlsx
Chiqish: data/*.json, data/branches_raw.txt (xom, hali normallashtirilmagan)

Keyingi qadam: build_database.py — shu xom fayllardan yakuniy carland.db yig'adi.

Talab qilinadigan kutubxonalar: pip install pymupdf pandas openpyxl
"""
import json
import re
from pathlib import Path

import pandas as pd
import pymupdf

BASE = Path(__file__).parent
RAW = BASE / "raw"
PDF_PATH = RAW / "Carland umumiy ma’lumotlar-3.pdf"
XLSX_PATH = RAW / "Aksiya SENTABR CALL SENTR.xlsx"

ZW = "​"


def clean(s):
    if s is None:
        return ""
    return re.sub(r"\s+", " ", s.replace(ZW, "")).strip()


def extract_pdf_tables(doc):
    # ---- 1. Motor/karobka/reduktor moy jadvali (sahifa 2-4, ustun soni 7) ----
    oil_rows = []
    for pno in [1, 2, 3]:
        for t in doc[pno].find_tables().tables:
            if t.col_count != 7:
                continue
            for row in t.extract():
                row = [clean(c) for c in row]
                if not row[0] or row[0].lower().startswith("mashina"):
                    continue
                oil_rows.append({
                    "model": row[0],
                    "engine_oil_volume_raw": row[1],
                    "gearbox_volume_raw": row[2],
                    "reductor_volume_raw": row[3],
                    "change_interval_km_raw": row[4],
                    "engine_oil_type_raw": row[5],
                    "gearbox_oil_type_raw": row[6],
                })
    json.dump(oil_rows, open(BASE / "oil_table_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("oil rows:", len(oil_rows))

    # ---- 2. Shina o'lchamlari (sahifa 14-23ish, ustun soni 8, yil oralig'i bor qatorlar) ----
    tire_rows = []
    for pno in range(13, 24):
        for t in doc[pno].find_tables().tables:
            if t.col_count != 8:
                continue
            for row in t.extract():
                row = [clean(c) for c in row]
                if re.search(r"(19|20)\d{2}", row[1]):
                    tire_rows.append({"model": row[0], "years": row[1], "sizes": [c for c in row[2:] if c]})
    json.dump(tire_rows, open(BASE / "tires_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("tire rows:", len(tire_rows))

    # ---- 3. Akkumulyatorlar (sahifa 8-11, ustun soni 4) ----
    battery_rows = []
    current = None
    for pno in range(7, 30):
        for t in doc[pno].find_tables().tables:
            if t.col_count != 4:
                continue
            for row in t.extract():
                row = [clean(c) for c in row]
                name, brand, price, car = row
                if name:
                    current = {"battery": name, "brand": brand, "price": price, "cars": []}
                    battery_rows.append(current)
                if car and current:
                    current["cars"].append(car)
    json.dump(battery_rows, open(BASE / "batteries_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("battery groups:", len(battery_rows))

    # ---- 4. Svecha (sahifa 5-6, ustun soni 6) ----
    svecha_rows = []
    for pno in [4, 5]:
        for t in doc[pno].find_tables().tables:
            if t.col_count != 6:
                continue
            for row in t.extract():
                row = [clean(c) for c in row]
                if not row[0] or "SVECHALAR" in row[0].upper() or row[0].upper() == "AVTO":
                    continue
                svecha_rows.append(row)
    json.dump(svecha_rows, open(BASE / "svecha_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("svecha rows:", len(svecha_rows))

    # ---- 5. Antifriz — UCHTA brend (VALESCO/FELIX/ZITRON), brand ustuni bilan ajratilgan ----
    antifreeze_rows = []
    current_brand = None
    for pno in [5, 6, 7]:
        for t in doc[pno].find_tables().tables:
            if t.col_count != 8:
                continue
            for row in t.extract():
                row = [clean(c) for c in row]
                first = row[0]
                rest_empty = all(not c for c in row[1:])
                if first and rest_empty and ("ANTFRIZ" in first.upper() or "ANTFREZ" in first.upper()):
                    current_brand = first
                    continue
                if not first or first.upper() == "AVTO":
                    continue
                antifreeze_rows.append({
                    "brand": current_brand, "model": first, "bachok_price": row[1],
                    "antfreeze_red": row[2], "antfreeze_blue": row[3], "liters": row[4],
                    "service_price": row[5], "summa_qizil": row[6], "summa_kok": row[7],
                })
    json.dump(antifreeze_rows, open(BASE / "antifreeze_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("antifreeze rows:", len(antifreeze_rows))

    # ---- 6. Filiallar matni (sahifa 1-2) ----
    p1 = doc[0].get_text()
    p2 = doc[1].get_text()
    branch_text = p1 + "\n" + p2.split("Mashinaga moylarni")[0]
    (BASE / "branches_raw.txt").write_text(branch_text, encoding="utf-8")
    print("branch text chars:", len(branch_text))


PRICE_RE = re.compile(r"^[\d\s]{2,}[.,]\d{2}\s*$")
SECTION_RE = re.compile(r"^(.{2,60}?)\s*\((\d+)\)\s*$")


def extract_product_catalog(doc):
    """Sahifa 24 dan oxirigacha: filtr/moy/ehtiyot qism/avtokimyo katalogi.
    Format: [nom qatorlari] 'Единица' [kategoriya qatorlari] [narx, masalan '135 000,00']
    Ba'zi bo'limlarda (ehtiyot qism, shina) 'Единица' yo'q — bunday holda joriy
    bo'lim sarlavhasidan ('Xxxx (NN)' shaklidagi) kategoriya olinadi."""
    products = []
    current_category = None
    name_buf, cat_buf, unit_seen = [], [], False

    def flush(price):
        nonlocal name_buf, cat_buf, unit_seen
        name = clean(" ".join(name_buf))
        cat = clean(" ".join(cat_buf)) if (unit_seen and cat_buf) else (current_category or "")
        if name:
            products.append({"name": name, "category": cat, "price": clean(price)})
        name_buf, cat_buf, unit_seen = [], [], False

    for pno in range(23, len(doc)):
        for line in [clean(l) for l in doc[pno].get_text().splitlines()]:
            if not line:
                continue
            if line == "Единица":
                unit_seen = True
                continue
            # Shina (balon) bo'limi boshqa bo'limlardan farqli — sarlavhasi
            # "Xxx (NN)" shaklida emas, "Balonlar razmeri va narxi" deb
            # yozilgan va undan keyin bir nechta izoh/jadval sarlavha
            # qatori keladi ("Hisoblab narx...", "Имя", "Цена продажи").
            # Bularni tanimasak, oldingi bo'limning kategoriyasi (masalan
            # "Transmission oils") barcha shina narxlariga yopishib qolib,
            # shinalar butunlay noto'g'ri toifada "yashirin" qolib ketadi.
            if line.upper().startswith("BALONLAR RAZMERI"):
                current_category = "Tires"
                name_buf, cat_buf, unit_seen = [], [], False
                continue
            if line.upper() in ("ИМЯ", "ЦЕНА ПРОДАЖИ") or "HISOBLAB NARX" in line.upper():
                continue
            m = SECTION_RE.match(line)
            if m and not unit_seen and not name_buf:
                current_category = clean(m.group(1))
                continue
            if PRICE_RE.match(line):
                flush(line)
                continue
            (cat_buf if unit_seen else name_buf).append(line)
        if len(name_buf) > 6:  # sahifa chegarasida qolib ketgan chala yozuvni tashlaymiz
            name_buf, cat_buf, unit_seen = [], [], False

    json.dump(products, open(BASE / "products_catalog_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("total products parsed:", len(products))


def extract_promotions_xlsx():
    xls = pd.ExcelFile(XLSX_PATH)
    result = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(XLSX_PATH, sheet_name=sheet, header=None).dropna(how="all")
        title = str(df.iloc[0, 0]).strip()
        headers = [str(x).strip() if pd.notna(x) else "" for x in df.iloc[1].tolist()]
        rows = []
        for _, r in df.iloc[2:].iterrows():
            vals = r.tolist()
            if all(pd.isna(v) for v in vals):
                continue
            row = {h: (None if pd.isna(v) else (str(v).strip() if isinstance(v, str) else v))
                   for h, v in zip(headers, vals) if h}
            if any(v not in (None, "") for v in row.values()):
                rows.append(row)
        result[sheet.strip()] = {"title": title, "rows": rows}
    json.dump(result, open(BASE / "promotions_sentabr.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    for k, v in result.items():
        print(k, "->", len(v["rows"]), "qator")


if __name__ == "__main__":
    doc = pymupdf.open(PDF_PATH)
    extract_pdf_tables(doc)
    extract_product_catalog(doc)
    extract_promotions_xlsx()
    print("\nXom fayllar tayyor. Endi: python3 build_database.py")
