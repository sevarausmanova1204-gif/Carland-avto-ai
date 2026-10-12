"""Google Sheets jadvalidan (CSV) mashinalarga svecha / kolodka / balon / antifriz
ma'lumotini va yangi mashinalarning moy hajmlarini bazaga kiritadi.

Ishlatilishi:
    1) Google Sheets: Fayl -> Yuklab olish -> CSV
    2) cd data && python3 import_parts_sheet.py yuklab_olingan.csv
    3) python3 build_database.py        (bazani qayta yig'adi)

Nima qiladi:
  - "№" ustuni sheet_row_map.json orqali qatorni bazadagi mashinalarga bog'laydi
    (bitta qator bir nechta dvigatel variantiga tegishli bo'lishi mumkin).
  - Kiritilgan svecha/kolodka/balon/antifriz -> car_parts_raw.json
    (shu mashina/qism uchun avvalgi yozuvlar jadvaldagi bilan almashtiriladi,
     jadvalda bo'sh qoldirilgan qismlarga TEGILMAYDI).
  - Bazada YO'Q mashina qatorida biror ma'lumot kiritilgan bo'lsa -> yangi mashina
    oil_table_raw.json oxiriga qo'shiladi (mavjud mashinalar ID'si o'zgarmaydi).
  - Bazada BOR mashinaning moy hajmi o'zgartirilgan bo'lsa — bu avtomatik
    qo'llanmaydi, import_report.txt ga "qo'lda ko'rib chiqing" deb yoziladi.

"Narx" kataklariga "35 000", "35000" yoki "35,000" yozish mumkin. Svecha/kolodka
nom katagiga bir nechta variantni ";" bilan va har birining narxini "= narx"
ko'rinishida yozish mumkin: "NGK ZFR6U = 35000; BOSCH 0242 = 40000".
"""
import csv
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

COL = {
    "no": "№", "holat": "Holat", "model": "Model",
    "eng_size": "Dvigatel hajmi/turi", "eng_l": "Motor moyi L", "eng_t": "Motor moyi turi",
    "gb_kind": "Karobka turi", "gb_l": "Karobka moyi L", "gb_t": "Karobka moyi turi",
    "rd_l": "Reduktor moyi L", "rd_t": "Reduktor moyi turi", "km": "Almashtirish km",
    "sp_name": "SVECHA: markasi/artikuli", "sp_qty": "SVECHA: soni (dona)", "sp_price": "SVECHA: narxi",
    "br_old": "KOLODKA: old markasi/artikuli", "br_old_p": "KOLODKA: old narxi",
    "br_rear": "KOLODKA: orqa markasi/artikuli", "br_rear_p": "KOLODKA: orqa narxi",
    "ti_size": "BALON: asosiy o'lcham", "ti_alt": "BALON: muqobil o'lchamlar",
    "ti_brand": "BALON: tavsiya brend/model", "ti_price": "BALON: narxi (dona)",
    "af_type": "ANTIFRIZ: turi (G11/G12/G12+)", "af_l": "ANTIFRIZ: hajmi (L)",
    "af_brand": "ANTIFRIZ: tavsiya brend", "af_price": "ANTIFRIZ: narxi",
}


def to_int(s):
    digits = re.sub(r"\D", "", s or "")
    return int(digits) if digits else None


def to_float(s):
    s = (s or "").strip().replace(",", ".")
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def named_items(cell, default_price=None):
    """'A = 35000; B = 40000' -> [(A, 35000), (B, 40000)]; narx bo'lmasa default."""
    out = []
    for seg in re.split(r"[;\n]+", cell or ""):
        seg = seg.strip()
        if not seg:
            continue
        name, price = seg, default_price
        if "=" in seg:
            name, _, p = seg.rpartition("=")
            price = to_int(p) or default_price
        out.append((name.strip(), price))
    return out


def parts_from_row(g):
    parts = {}
    sp = [{"name": n, "qty": to_int(g("sp_qty")), "price": p}
          for n, p in named_items(g("sp_name"), to_int(g("sp_price")))]
    if sp:
        parts["spark"] = sp
    br = [{"position": "old", "name": n, "price": p} for n, p in named_items(g("br_old"), to_int(g("br_old_p")))]
    br += [{"position": "orqa", "name": n, "price": p} for n, p in named_items(g("br_rear"), to_int(g("br_rear_p")))]
    if br:
        parts["brake"] = br
    if g("ti_size") or g("ti_alt"):
        alts = [a.strip() for a in re.split(r"[,;\n]+", g("ti_alt")) if a.strip()]
        parts["tire"] = [{"size": g("ti_size"), "alt_sizes": alts, "brand": g("ti_brand"), "price": to_int(g("ti_price"))}]
    if g("af_type") or g("af_l") or g("af_brand"):
        parts["antifreeze"] = [{"type": g("af_type"), "liters": to_float(g("af_l")), "brand": g("af_brand"),
                                "price": to_int(g("af_price"))}]
    return parts


def oil_raw_row(model, g):
    """Jadval kataklarini oil_table_raw.json formatidagi qatorga aylantiradi."""
    def vol(l, t=""):
        if not g(l):
            return ""
        return f"{g(l)} litr" + (f" {g(t)}" if t and g(t) else "")
    gb = ""
    if g("gb_l"):
        gb = " ".join(x for x in (g("gb_kind"), f"{g('gb_l')} litr", g("gb_t")) if x)
    rd = f"{g('rd_l')} litr" if g("rd_l") else ""
    return {
        "model": model,
        "engine_oil_volume_raw": vol("eng_l"),
        "gearbox_volume_raw": gb,
        "reductor_volume_raw": rd,
        "change_interval_km_raw": g("km"),
        "engine_oil_type_raw": g("eng_t"),
        "gearbox_oil_type_raw": g("gb_t"),
        **({"reductor_oil_type_raw": g("rd_t")} if g("rd_t") else {}),
    }


def main(csv_path):
    row_map = json.loads((BASE / "sheet_row_map.json").read_text(encoding="utf-8"))
    parts_path = BASE / "car_parts_raw.json"
    oil_path = BASE / "oil_table_raw.json"
    parts_raw = json.loads(parts_path.read_text(encoding="utf-8")) if parts_path.exists() else []
    oil_raw = json.loads(oil_path.read_text(encoding="utf-8"))
    existing_models = {r["model"] for r in oil_raw}
    index = {(r["model"], r["part"]): r for r in parts_raw}

    report, new_cars, updated = [], 0, 0
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            def g(key, row=row):
                return (row.get(COL[key]) or "").strip()

            no = g("no")
            info = row_map.get(no)
            model_name = g("model") or (info or {}).get("model", "")
            parts = parts_from_row(g)
            oil_filled = any(g(k) for k in ("eng_l", "eng_t", "gb_l", "gb_t", "rd_l", "rd_t", "km"))
            if not parts and not oil_filled:
                continue

            car_models = list((info or {}).get("car_models") or [])
            if not car_models:
                # bazada yo'q mashina -> yangi mashina sifatida qo'shiladi
                if model_name and model_name not in existing_models:
                    oil_raw.append(oil_raw_row(model_name, g))
                    existing_models.add(model_name)
                    new_cars += 1
                car_models = [model_name]
            elif oil_filled:
                report.append(f"№{no} {model_name}: moy ma'lumoti kiritilgan, lekin mashina bazada BOR — "
                              f"qo'lda ko'rib chiqing (oil_table_raw.json): {', '.join(car_models)}")

            for cm in car_models:
                for part, items in parts.items():
                    index[(cm, part)] = {"model": cm, "part": part, "items": items}
                    updated += 1

    out = sorted(index.values(), key=lambda r: (r["model"], r["part"]))
    parts_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    oil_path.write_text(json.dumps(oil_raw, ensure_ascii=False, indent=2), encoding="utf-8")
    (BASE / "import_report.txt").write_text("\n".join(report) + ("\n" if report else ""), encoding="utf-8")
    print(f"Yangi mashinalar: {new_cars} | yozilgan qism yozuvlari: {updated} | qo'lda ko'rish: {len(report)}")
    print("Keyingi qadam: python3 build_database.py")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Ishlatilishi: python3 import_parts_sheet.py jadval.csv")
    main(sys.argv[1])
