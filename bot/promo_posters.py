"""Aksiya paketlarining rasmli plakatlari (oktabr aksiyalari).

Plakatlar data/promotions_sentabr.json dagi jadvallardan chiziladi va
assets/promos/ papkasiga PNG sifatida saqlanadi (bot ularni tayyor fayl
sifatida yuboradi). Qayta chizish:

    python3 -m bot.promo_posters

Aksiyaning amal qilish muddati (AKSIYA MUDDATI, "dd.mm.yyyy gacha") o'tgan
bo'lsa, paket "faol" hisoblanmaydi va botda ko'rsatilmaydi.
"""
import json
import re
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT_DIR = ROOT / "assets" / "promos"
DATA = ROOT / "data" / "promotions_sentabr.json"

SKIP_SHEETS = ("SVECHA GM", "ANTFRIZ UMUMIY", "AKKUMULATOR")

W = 1080
PAD = 48
BG = (10, 14, 22)
PANEL = (19, 26, 38)
PANEL_ALT = (25, 33, 47)
LINE = (44, 56, 76)
AMBER = (255, 176, 32)       # CARLAND brend rangi
AMBER_DARK = (46, 32, 4)
WHITE = (240, 244, 250)
MUTED = (140, 153, 172)
GREEN = (92, 214, 150)

DATE_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")

BONUS_LABELS = [
    ("MOY FILTER", "Moy filtri"),
    ("AIR FILTER", "Havo filtri"),
    ("SALON FILTER", "Salon filtri"),
    ("DELFIN SOCHIQ", "Delfin sochiq"),
    ("OSVIJITEL", "Osvijitel"),
    ("OYNA SUVI", "Oyna suvi"),
    ("GETSUN", "Getsun"),
    ("USLUGA", "Almashtirish xizmati"),
]


def _font(bold: bool, size: int):
    p = FONTS / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(str(p), size) if p.exists() else ImageFont.load_default()


def slug_for(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")


def poster_path(key: str) -> Path:
    return OUT_DIR / f"{slug_for(key)}.png"


def parse_deadline(text) -> date | None:
    m = DATE_RE.search(str(text or ""))
    if not m:
        return None
    try:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None


def is_active(details: dict, today: date | None = None) -> bool:
    """Muddati ko'rsatilmagan yoki hali o'tmagan aksiya — faol."""
    d = parse_deadline((details or {}).get("AKSIYA MUDDATI"))
    return d is None or d >= (today or date.today())


def load_packages() -> dict:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    return {k: v for k, v in payload.items() if k not in SKIP_SHEETS}


def clean_title(title: str) -> str:
    t = re.sub(r"^\s*(АКЦИЯ|AKSIYA)\s+", "", title.strip(), flags=re.I)
    return t


def active_packages(today: date | None = None) -> list[tuple[str, str, Path]]:
    """[(key, title, poster_path)] — muddati o'tmagan paketlar, fayli bor bo'lsa."""
    out = []
    for key, pkg in load_packages().items():
        rows = pkg.get("rows") or []
        if not rows or not any(is_active(r, today) for r in rows):
            continue
        path = poster_path(key)
        if path.exists():
            out.append((key, clean_title(pkg["title"]), path))
    return out


def package_key_for_title(title: str) -> str | None:
    for key, pkg in load_packages().items():
        if pkg.get("title") == title:
            return key
    return None


def _money(n) -> str:
    try:
        return f"{int(round(float(n))):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(n)


def _liters(v) -> str:
    try:
        f = float(v)
        return f"{f:g}".replace(".", ",")
    except (TypeError, ValueError):
        return str(v)


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _codes(row: dict) -> str:
    """"MF 003 BONUS" -> "MF 003" (filtr artikullari) — faqat kodi bor qiymatlar."""
    parts = []
    for k in ("MOY FILTER", "AIR FILTER", "SALON FILTER"):
        v = str(row.get(k, ""))
        v = re.sub(r"\bBONUS\b", "", v).strip()
        if v and not v.isdigit():
            parts.append(v)
    return " · ".join(parts)


def render(key: str, pkg: dict) -> Image.Image:
    rows = pkg["rows"]
    title = clean_title(pkg["title"])
    is_ev = "ITOG" in rows[0]
    deadline = next((r.get("AKSIYA MUDDATI") for r in rows if r.get("AKSIYA MUDDATI")), "")
    note = next((r.get("IZOH") for r in rows if r.get("IZOH")), "")
    has_codes = any(_codes(r) for r in rows)

    # ---- ustunlar ----
    if is_ev:
        cols = [("Avtomobil", "AVTO", 0.33, "l"), ("Reduktor\nmoyi, L", "MOY", 0.10, "r"),
                ("Moy", "MOY SUMMA", 0.12, "r"), ("Filtr", "MOY FILTER", 0.10, "r"),
                ("Xizmat", "USLUGA", 0.11, "r"), ("Jami", "ITOG", 0.12, "r"), ("-15%\nbilan", "ITOG (-15%)", 0.12, "r")]
    elif has_codes:
        cols = [("Avtomobil", "AVTO", 0.27, "l"), ("Moy, L", "MOY", 0.10, "r"),
                ("Narx, so'm", "MOY SUMMA", 0.19, "r"), ("Sovg'a filtrlar", "_codes", 0.44, "l")]
    else:
        cols = [("Avtomobil", "AVTO", 0.46, "l"), ("Moy, L", "MOY", 0.18, "r"), ("Narx, so'm", "MOY SUMMA", 0.36, "r")]

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    f_title, f_sub = _font(True, 46), _font(False, 28)
    f_head, f_cell, f_cellb = _font(True, 24), _font(False, 28), _font(True, 30)
    f_chip, f_small = _font(True, 26), _font(False, 22)
    inner = W - 2 * PAD

    title_lines = _wrap(probe, title, f_title, inner)
    # ---- balandlikni hisoblash ----
    y = 150 + 36
    h_title = len(title_lines) * 58
    gifts = []
    for k, label in BONUS_LABELS:
        vals = [r.get(k) for r in rows if r.get(k) not in (None, "")]
        if not vals:
            continue
        # narxi yozilgan (pulli) qiymatlar sovg'a emas — jadvalda ko'rsatiladi
        if any(isinstance(v, (int, float)) for v in vals):
            continue
        text = label
        if k == "USLUGA":
            text = "Almashtirish xizmati — bepul"
        gifts.append(text)
    gift_cols = 2
    gift_rows_n = (len(gifts) + gift_cols - 1) // gift_cols
    h_gifts = (82 + 54 + gift_rows_n * 68 + 20) if gifts else 0
    h_cash = 230
    row_h = 66 if has_codes or is_ev else 60
    head_h = 78 if is_ev else 56
    h_table = head_h + len(rows) * row_h
    note_lines = _wrap(probe, note, f_small, inner - 40) if note else []
    h_note = (len(note_lines) * 30 + 40) if note_lines else 0
    total = y + h_title + 90 + h_gifts + (30 if gifts else 0) + 56 + h_table + 36 + h_note + h_cash + 150

    img = Image.new("RGB", (W, total), BG)
    d = ImageDraw.Draw(img)

    # yuqori panel
    d.rectangle([0, 0, W, 130], fill=AMBER)
    d.text((PAD, 28), "CARLAND", font=_font(True, 56), fill=AMBER_DARK)
    tag = "OKTABR AKSIYASI"
    d.text((W - PAD - d.textlength(tag, font=_font(True, 34)), 46), tag, font=_font(True, 34), fill=AMBER_DARK)
    # sarlavha
    ty = 180
    for ln in title_lines:
        d.text((PAD, ty), ln, font=f_title, fill=WHITE)
        ty += 58
    # muddat belgisi
    if deadline:
        label = f"{deadline} amal qiladi"
        bw = int(d.textlength(label, font=f_head)) + 40
        d.rounded_rectangle([PAD, ty + 14, PAD + bw, ty + 14 + 48], radius=24, outline=AMBER, width=3)
        d.text((PAD + 20, ty + 14 + 11), label, font=f_head, fill=AMBER)
    ty += 90
    # sovg'alar bloki (alohida, yashil, ko'zga tashlanadigan)
    if gifts:
        GREEN_DARK = (17, 38, 31)
        d.rounded_rectangle([PAD, ty, W - PAD, ty + h_gifts], radius=22, fill=GREEN_DARK, outline=GREEN, width=4)
        d.rounded_rectangle([PAD, ty, W - PAD, ty + 82], radius=22, fill=GREEN)
        d.rectangle([PAD, ty + 50, W - PAD, ty + 82], fill=GREEN)
        # sovg'a quti belgisi
        gx, gy = PAD + 24, ty + 14
        d.rounded_rectangle([gx, gy + 18, gx + 56, gy + 54], radius=6, fill=(17, 38, 31))
        d.rectangle([gx - 4, gy + 10, gx + 60, gy + 24], fill=(17, 38, 31))
        d.rectangle([gx + 24, gy + 10, gx + 32, gy + 54], fill=GREEN)
        d.ellipse([gx + 8, gy - 4, gx + 30, gy + 14], outline=(17, 38, 31), width=5)
        d.ellipse([gx + 26, gy - 4, gx + 48, gy + 14], outline=(17, 38, 31), width=5)
        d.text((PAD + 104, ty + 17), "SOVG'A — BEPUL BERILADI", font=_font(True, 40), fill=(17, 38, 31))
        d.text((PAD + 24, ty + 96), "Moy narxiga kiritilgan, alohida to'lanmaydi", font=f_small, fill=MUTED)
        gy = ty + 82 + 54
        colw = (inner - 48) // gift_cols
        for i, g in enumerate(gifts):
            cx = PAD + 24 + (i % gift_cols) * colw
            cy = gy + (i // gift_cols) * 68
            d.rounded_rectangle([cx, cy, cx + colw - 14, cy + 56], radius=14, fill=(26, 66, 49), outline=GREEN, width=2)
            d.text((cx + 16, cy + 12), "✓", font=f_chip, fill=GREEN)
            gtxt = g
            gf = _font(True, 26)
            while d.textlength(gtxt, font=gf) > colw - 14 - 64 and gf.size > 18:
                gf = _font(True, gf.size - 1)
            d.text((cx + 52, cy + 14), gtxt, font=gf, fill=WHITE)
        ty += h_gifts + 30
    d.text((PAD, ty), "MOY NARXI (sovg'alar bilan birga)", font=f_head, fill=MUTED)
    ty += 40

    # jadval
    d.rounded_rectangle([PAD, ty, W - PAD, ty + h_table], radius=18, fill=PANEL, outline=LINE, width=2)
    xs, x = [], PAD
    for _, _, frac, _ in cols:
        xs.append(x)
        x += inner * frac
    xs.append(W - PAD)
    for i, (label, _, _, align) in enumerate(cols):
        for j, part in enumerate(label.split("\n")):
            tw = d.textlength(part, font=f_head)
            tx = xs[i] + 18 if align == "l" else xs[i + 1] - 18 - tw
            d.text((tx, ty + 14 + j * 28), part, font=f_head, fill=AMBER)
    d.line([PAD + 12, ty + head_h - 4, W - PAD - 12, ty + head_h - 4], fill=LINE, width=2)
    def cell(r, field):
        if field == "AVTO":
            return str(r.get("AVTO", "")), True, WHITE
        if field == "_codes":
            return _codes(r), False, MUTED
        if field == "MOY":
            return _liters(r.get("MOY", "")), False, WHITE
        v = r.get(field, "")
        if isinstance(v, (int, float)):
            text = _money(v)
        else:
            text = "bonus" if "BONUS" in str(v).upper() or str(v).upper() == "BEPUL" else str(v)
        strong = field in ("MOY SUMMA", "ITOG (-15%)")
        color = AMBER if strong else (GREEN if text == "bonus" else WHITE)
        return text, strong, color

    # har bir ustun uchun BITTA shrift o'lchami: eng uzun qiymat sig'adigan eng katta o'lcham
    col_fonts = []
    for i, (_, field, _, _) in enumerate(cols):
        maxw = xs[i + 1] - xs[i] - 30
        size = 22 if field == "_codes" else (26 if is_ev else 30)
        bold = cell(rows[0], field)[1]
        while size > 14:
            f = _font(any(cell(r, field)[1] for r in rows), size)
            if all(d.textlength(cell(r, field)[0], font=f) <= maxw for r in rows):
                break
            size -= 1
        col_fonts.append((_font(any(cell(r, field)[1] for r in rows), size), size))

    ry = ty + head_h
    for n, r in enumerate(rows):
        if n % 2 and n < len(rows) - 1:
            d.rectangle([PAD + 3, ry, W - PAD - 3, ry + row_h], fill=PANEL_ALT)
        for i, (_, field, _, align) in enumerate(cols):
            text, _, color = cell(r, field)
            f, size = col_fonts[i]
            tw = d.textlength(text, font=f)
            tx = xs[i] + 18 if align == "l" else xs[i + 1] - 18 - tw
            d.text((tx, ry + (row_h - size) // 2 - 4), text, font=f, fill=color)
        ry += row_h
    ty = ry + 36

    if note_lines:
        d.rounded_rectangle([PAD, ty, W - PAD, ty + h_note - 12], radius=14, fill=AMBER_DARK, outline=AMBER, width=2)
        for i, ln in enumerate(note_lines):
            d.text((PAD + 20, ty + 20 + i * 30), ln, font=f_small, fill=AMBER)
        ty += h_note

    # keshbek bandi
    ty += 10
    d.rounded_rectangle([PAD, ty, W - PAD, ty + 184], radius=20, fill=AMBER)
    d.text((PAD + 28, ty + 18), "5% KESHBEK", font=_font(True, 46), fill=AMBER_DARK)
    d.text((PAD + 28, ty + 76), "Carland ilovasini yuklab oling: birinchi xaridingizga 5% qaytadi.", font=_font(True, 25), fill=AMBER_DARK)
    d.text((PAD + 28, ty + 110), "Misol: 500 000 so'mlik xarid  →  25 000 so'm sizga qaytadi.", font=_font(True, 25), fill=AMBER_DARK)
    d.text((PAD + 28, ty + 144), "Ilova: App Store va Google Play, «Carland».", font=_font(False, 24), fill=AMBER_DARK)

    # pastki qism
    d.line([PAD, total - 120, W - PAD, total - 120], fill=LINE, width=2)
    d.text((PAD, total - 98), "Narx va moslikni filialda tasdiqlang.", font=f_sub, fill=WHITE)
    d.text((PAD, total - 58), "Carland bot  ·  Aksiyalar  ·  Mashina bo'yicha", font=f_small, fill=MUTED)
    return img


def build_all() -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    made = []
    for key, pkg in load_packages().items():
        if not pkg.get("rows"):
            continue
        path = poster_path(key)
        render(key, pkg).save(path, optimize=True)
        made.append(path)
    return made


if __name__ == "__main__":
    for p in build_all():
        print(p.relative_to(ROOT))
