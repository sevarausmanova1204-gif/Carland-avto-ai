"""Har bir mashina rusumi uchun motor / karobka / reduktor haqidagi
"exploded-view" uslubidagi vektor-chizma (blueprint) infografika generatori.

MUHIM: bu haqiqiy mashina yoki uning dvigateli FOTOSI EMAS. Bu — umumiy
porshenli dvigatel/uzatmalar qutisi anatomiyasini ko'rsatuvchi texnik
chizma (har qanday dvigatel uchun umumiy tuzilma), ustiga esa shu aniq
mashina rusumi uchun bazadagi HAQIQIY raqamlar (moy hajmi, turi,
almashtirish oralig'i) qo'yilgan. Chizma qismlari ("silindrlar bloki",
"krivoshipli-shatun mexanizmi" va h.k.) — umumiy avtomobil anatomiyasi
atamalari, aynan shu modelning tashqi ko'rinishi haqida da'vo emas.
"""
import io
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "fonts"

W = 1200

BG = (9, 12, 18)
GRID = (18, 23, 32)
PANEL = (16, 21, 30)
PANEL_BORDER = (34, 42, 56)
ACCENT = (0, 209, 255)       # ko'k-siyanid — chizma chizig'i rangi
ACCENT_2 = (255, 176, 32)    # CARLAND brend rangi
TEXT_MAIN = (232, 238, 245)
TEXT_MUTED = (128, 140, 158)
RED = (255, 99, 99)
GREEN = (86, 214, 150)


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = ASSETS / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def F_TITLE(s=44):
    return _font("DejaVuSans-Bold.ttf", s)


def F_BOLD(s=28):
    return _font("DejaVuSans-Bold.ttf", s)


def F_REG(s=24):
    return _font("DejaVuSans.ttf", s)


# ---------------------------------------------------------------- iso helpers

COS30, SIN30 = math.cos(math.radians(30)), math.sin(math.radians(30))


def iso(ox, oy, x, y, z, scale=1.0):
    sx = ox + (x - z) * COS30 * scale
    sy = oy + (x + z) * SIN30 * scale - y * scale
    return (sx, sy)


def draw_iso_box(draw, ox, oy, w, h, d, scale=1.0, color=ACCENT, width=4, top_fill=None, front_fill=None, side_fill=None):
    pts = {}
    for bx in (0, w):
        for by in (0, h):
            for bz in (0, d):
                pts[(bx, by, bz)] = iso(ox, oy, bx, by, bz, scale)

    top = [pts[(0, h, 0)], pts[(w, h, 0)], pts[(w, h, d)], pts[(0, h, d)]]
    front = [pts[(0, 0, 0)], pts[(w, 0, 0)], pts[(w, h, 0)], pts[(0, h, 0)]]
    side = [pts[(w, 0, 0)], pts[(w, 0, d)], pts[(w, h, d)], pts[(w, h, 0)]]

    if top_fill:
        draw.polygon(top, fill=top_fill)
    if front_fill:
        draw.polygon(front, fill=front_fill)
    if side_fill:
        draw.polygon(side, fill=side_fill)

    edges = [
        ((0, 0, 0), (w, 0, 0)), ((w, 0, 0), (w, 0, d)), ((w, 0, d), (0, 0, d)), ((0, 0, d), (0, 0, 0)),
        ((0, h, 0), (w, h, 0)), ((w, h, 0), (w, h, d)), ((w, h, d), (0, h, d)), ((0, h, d), (0, h, 0)),
        ((0, 0, 0), (0, h, 0)), ((w, 0, 0), (w, h, 0)), ((w, 0, d), (w, h, d)), ((0, 0, d), (0, h, d)),
    ]
    for a, b in edges:
        draw.line([pts[a], pts[b]], fill=color, width=width)
    return pts


def draw_iso_cylinder_bump(draw, ox, oy, x, z, r, height, scale, color):
    top_c = iso(ox, oy, x, height, z, scale)
    bot_c = iso(ox, oy, x, 0, z, scale)
    rx, ry = r * scale, r * scale * 0.5
    draw.line([bot_c, top_c], fill=color, width=3)
    draw.line([(bot_c[0] - rx, bot_c[1]), (top_c[0] - rx, top_c[1])], fill=color, width=3)
    draw.line([(bot_c[0] + rx, bot_c[1]), (top_c[0] + rx, top_c[1])], fill=color, width=3)
    draw.ellipse([top_c[0] - rx, top_c[1] - ry, top_c[0] + rx, top_c[1] + ry], outline=color, width=3)


def draw_gear(draw, cx, cy, r, color, teeth=10, width=4):
    outer, inner, hub = r, r * 0.74, r * 0.3
    pts = []
    for i in range(teeth * 2):
        ang = math.pi * i / teeth
        rad = outer if i % 2 == 0 else inner
        pts.append((cx + rad * math.sin(ang), cy - rad * math.cos(ang)))
    draw.polygon(pts, outline=color, width=width)
    draw.ellipse([cx - hub, cy - hub, cx + hub, cy + hub], outline=color, width=width)


def draw_grid_bg(img):
    draw = ImageDraw.Draw(img)
    step = 48
    w, h = img.size
    for x in range(0, w, step):
        draw.line([(x, 0), (x, h)], fill=GRID, width=1)
    for y in range(0, h, step):
        draw.line([(0, y), (w, y)], fill=GRID, width=1)


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def leader_label(draw, anchor, text_y, text, font, side="left", color=TEXT_MAIN, margin=20):
    """side='left': matn chap chekkadan boshlanadi (o'qish yo'nalishi normal).
    side='right': matn o'ng chekkada tugaydi (o'ngga tekislangan)."""
    tw = draw.textlength(text, font=font)
    if side == "left":
        text_x = margin
        knee = (text_x + tw + 14, text_y)
    else:
        text_x = W - margin - tw
        knee = (text_x - 14, text_y)

    draw.line([anchor, knee], fill=ACCENT, width=2)
    r = 5
    draw.ellipse([anchor[0] - r, anchor[1] - r, anchor[0] + r, anchor[1] + r], fill=ACCENT)
    draw.ellipse([knee[0] - 3, knee[1] - 3, knee[0] + 3, knee[1] + 3], fill=ACCENT)
    draw.text((text_x, text_y - font.size // 2), text, font=font, fill=color)


# ------------------------------------------------------------- illustration

def draw_electric_motor_icon(draw, ox, oy, scale, color):
    """Elektromobillar uchun ICE (benzin dvigateli) chizmasi o'rniga
    soddalashtirilgan elektr dvigateli belgisi (aylana + chaqmoq)."""
    c = iso(ox, oy, 100, 65, 85, scale)
    r = 95
    draw.ellipse([c[0] - r, c[1] - r * 0.62, c[0] + r, c[1] + r * 0.62], outline=color, width=4)
    draw.ellipse([c[0] - r * 0.6, c[1] - r * 0.37, c[0] + r * 0.6, c[1] + r * 0.37], outline=color, width=3)
    bolt = [
        (c[0] - 10, c[1] - 40), (c[0] + 14, c[1] - 6), (c[0] - 2, c[1] - 6),
        (c[0] + 10, c[1] + 40), (c[0] - 14, c[1] + 2), (c[0] + 2, c[1] + 2),
    ]
    draw.polygon(bolt, fill=ACCENT_2)
    return c


def draw_engine_gearbox_illustration(draw, cx, cy, gearbox_kind: str, has_reductor: bool, is_ev: bool = False):
    """Markazda motor + karobka (+ reduktor) ning izometrik chizmasini
    chizadi va leader-line yorliqlari uchun anchor nuqtalarni qaytaradi."""
    scale = 1.0
    anchors = {}

    # --- MOTOR (chapda): ICE bo'lsa dvigatel bloki, EV bo'lsa elektr motor belgisi ---
    block_ox, block_oy = cx - 330, cy + 40

    if is_ev:
        anchors["electric"] = draw_electric_motor_icon(draw, block_ox, block_oy, scale, ACCENT)
    else:
        draw_iso_box(draw, block_ox, block_oy, 200, 130, 170, scale, color=ACCENT, width=4)
        anchors["block"] = iso(block_ox, block_oy, 100, 130, 0, scale)

        # silindr bumplari (valve cover ustida)
        for i, fx in enumerate((45, 100, 155)):
            draw_iso_cylinder_bump(draw, block_ox, block_oy, fx, 90, 16, 55, scale, ACCENT)
        anchors["cylinders"] = iso(block_ox, block_oy, 100, 145, 45, scale)

        # gaz taqsimlash (kamshaft) chizig'i — valve cover ustidagi gorizontal chiziq
        vc_l = iso(block_ox, block_oy, 20, 130, 20, scale)
        vc_r = iso(block_ox, block_oy, 180, 130, 20, scale)
        draw.line([vc_l, vc_r], fill=ACCENT_2, width=3)
        anchors["camshaft"] = iso(block_ox, block_oy, 100, 130, 20, scale)

        # krivoshipli-shatun (crankshaft) — blok ostida gorizontal chiziq + doiralar
        cs_y = block_oy + 40
        cs_x1, cs_x2 = block_ox + 10, block_ox + 190
        draw.line([(cs_x1, cs_y), (cs_x2, cs_y)], fill=ACCENT, width=4)
        for fx in (cs_x1 + 20, (cs_x1 + cs_x2) / 2, cs_x2 - 20):
            draw.ellipse([fx - 12, cs_y - 12, fx + 12, cs_y + 12], outline=ACCENT, width=3)
        anchors["crankshaft"] = (cs_x1 + 30, cs_y)

        # moy karteri (oil pan) — blok ostida kichik iso quti
        draw_iso_box(draw, block_ox + 20, block_oy - 55, 160, 35, 130, scale, color=GREEN, width=3)
        anchors["oilpan"] = iso(block_ox + 20, block_oy - 55, 80, 0, 65, scale)

    # --- ulash vali (motor -> karobka) ---
    shaft_y = block_oy - 20
    draw.line([(block_ox + 200, shaft_y), (cx + 60, shaft_y)], fill=ACCENT, width=5)

    # --- KAROBKA (o'ngda), turiga qarab ---
    gb_ox, gb_oy = cx + 60, block_oy
    kind = (gearbox_kind or "").lower()

    if "avtomat" in kind or "akpp" in kind:
        tc_c = (gb_ox + 10, gb_oy - 55)
        draw.ellipse([tc_c[0] - 45, tc_c[1] - 45, tc_c[0] + 45, tc_c[1] + 45], outline=ACCENT_2, width=4)
        draw.ellipse([tc_c[0] - 22, tc_c[1] - 22, tc_c[0] + 22, tc_c[1] + 22], outline=ACCENT_2, width=3)
        anchors["torque_conv"] = (tc_c[0], tc_c[1] - 45)
        draw_iso_box(draw, gb_ox + 90, gb_oy, 150, 120, 150, scale, color=ACCENT, width=4)
        anchors["gearbox"] = iso(gb_ox + 90, gb_oy, 75, 120, 0, scale)
    elif "variator" in kind or "cvt" in kind:
        p1 = (gb_ox + 40, gb_oy - 60)
        p2 = (gb_ox + 190, gb_oy - 60)
        for p in (p1, p2):
            draw.ellipse([p[0] - 38, p[1] - 38, p[0] + 38, p[1] + 38], outline=ACCENT_2, width=4)
        draw.line([(p1[0], p1[1] - 38), (p2[0], p2[1] - 38)], fill=ACCENT_2, width=4)
        draw.line([(p1[0], p1[1] + 38), (p2[0], p2[1] + 38)], fill=ACCENT_2, width=4)
        anchors["torque_conv"] = (p1[0], p1[1] - 38)
        draw_iso_box(draw, gb_ox + 10, gb_oy, 220, 60, 150, scale, color=ACCENT, width=4)
        anchors["gearbox"] = iso(gb_ox + 10, gb_oy, 110, 60, 0, scale)
    elif "elektromotor" in kind:
        draw_gear(draw, gb_ox + 110, gb_oy - 30, 55, ACCENT_2, width=4)
        anchors["torque_conv"] = (gb_ox + 110, gb_oy - 85)
        draw_iso_box(draw, gb_ox + 10, gb_oy, 200, 110, 150, scale, color=ACCENT, width=4)
        anchors["gearbox"] = iso(gb_ox + 10, gb_oy, 100, 110, 0, scale)
    else:  # Mexanika yoki nomaʼlum
        draw_iso_box(draw, gb_ox + 10, gb_oy, 190, 100, 150, scale, color=ACCENT, width=4)
        lever_top = iso(gb_ox + 10, gb_oy, 95, 100, 40, scale)
        lever_base = (lever_top[0], lever_top[1] + 55)
        draw.line([lever_base, lever_top], fill=ACCENT_2, width=4)
        draw.ellipse([lever_top[0] - 8, lever_top[1] - 8, lever_top[0] + 8, lever_top[1] + 8], fill=ACCENT_2)
        anchors["torque_conv"] = lever_top
        anchors["gearbox"] = iso(gb_ox + 10, gb_oy, 95, 100, 0, scale)

    # --- REDUKTOR (agar mavjud bo'lsa) — karobka ostida kichik blok ---
    if has_reductor:
        red_ox, red_oy = gb_ox + 40, gb_oy + 90
        draw_iso_box(draw, red_ox, red_oy, 120, 70, 120, scale, color=GREEN, width=3)
        rc = iso(red_ox, red_oy, 60, 35, 60, scale)
        draw.ellipse([rc[0] - 22, rc[1] - 22, rc[0] + 22, rc[1] + 22], outline=GREEN, width=3)
        anchors["reductor"] = iso(red_ox, red_oy, 60, 70, 0, scale)

    return anchors


# ------------------------------------------------------------------ stat card

def stat_card(draw, x, y, w, h, color, title, lines):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=20, fill=PANEL, outline=PANEL_BORDER, width=2)
    draw.rounded_rectangle([x, y, x + 10, y + h], radius=20, fill=color)
    draw.text((x + 30, y + 22), title, font=F_BOLD(30), fill=color)
    ty = y + 68
    for line in lines:
        draw.text((x + 30, ty), line, font=F_REG(25), fill=TEXT_MAIN)
        ty += 36


def generate_car_infographic(car: dict) -> bytes:
    from . import config

    is_ev = not car.get("engine_oil_liters") and not car.get("engine_oil_types")
    engine_line_count = 1 if is_ev else 3
    gb_line_count = 3 + (1 if car.get("gearbox_liters") else 0)
    red_line_count = 3
    engine_card_h = 34 * engine_line_count + 90
    gb_card_h = 34 * gb_line_count + 90
    if car.get("reductor_liters"):
        gb_card_h = max(gb_card_h, 34 * red_line_count + 90)
    cards_h = engine_card_h + 24 + gb_card_h
    dynamic_h = 930 + cards_h + 24 + 90  # header+illustration, kartalar, footer

    img = Image.new("RGB", (W, dynamic_h), BG)
    draw_grid_bg(img)
    draw = ImageDraw.Draw(img)

    # sarlavha
    draw.text((56, 40), "CARLAND", font=F_TITLE(38), fill=ACCENT_2)
    draw.text((W - 56, 44), "AVTOMATIK TEXNIK SXEMA", font=F_REG(20), fill=TEXT_MUTED, anchor="ra")
    draw.text((56, 92), car["model"], font=F_BOLD(48), fill=TEXT_MAIN)
    draw.text((56, 150), "Motor • Uzatmalar qutisi • Reduktor — moy ma'lumotlari", font=F_REG(22), fill=TEXT_MUTED)
    draw.line([56, 195, W - 56, 195], fill=PANEL_BORDER, width=2)

    gearbox_kind = car.get("gearbox_kind") or ""
    has_reductor = bool(car.get("reductor_liters"))
    illus_cy = 560
    anchors = draw_engine_gearbox_illustration(draw, W // 2, illus_cy, gearbox_kind, has_reductor, is_ev=is_ev)

    f_label = F_REG(23)
    if is_ev:
        leader_label(draw, anchors["electric"], 500, "Elektr dvigateli (motor moyi talab qilinmaydi)", f_label, side="left")
    else:
        leader_label(draw, anchors["cylinders"], 300, "Silindrlar bloki", f_label, side="left")
        leader_label(draw, anchors["camshaft"], 360, "Gaz taqsimlash tizimi", f_label, side="left")
        leader_label(draw, anchors["crankshaft"], 700, "Krivoshipli-shatun mexanizmi", f_label, side="left")
        leader_label(draw, anchors["oilpan"], 760, "Moy nasosi va moy karteri", f_label, side="left")

    kind_label = gearbox_kind or "Uzatmalar qutisi"
    leader_label(draw, anchors["gearbox"], 330, kind_label, f_label, side="right")
    if "torque_conv" in anchors:
        low = gearbox_kind.lower()
        if "avtomat" in low:
            tc_name = "Gidrotransformator"
        elif "variator" in low or "cvt" in low:
            tc_name = "Variator shkivlari (CVT)"
        elif "elektromotor" in low:
            tc_name = "Tortish motori uzeli"
        else:
            tc_name = "Uzatish richagi"
        leader_label(draw, anchors["torque_conv"], 400, tc_name, f_label, side="right")
    if has_reductor and "reductor" in anchors:
        leader_label(draw, anchors["reductor"], 760, "Reduktor (differensial)", f_label, side="right")

    draw.line([56, 900, W - 56, 900], fill=PANEL_BORDER, width=2)

    # --- pastki qismda: HAQIQIY raqamli ma'lumotlar (baza asosida) ---
    card_y = 930
    card_w = (W - 56 * 2 - 24) // 2 if has_reductor else (W - 112)

    engine_liters = car.get("engine_oil_liters")
    engine_types = car.get("engine_oil_types") or []
    if is_ev:
        lines = ["Elektr dvigateli — an'anaviy motor moyi talab qilinmaydi"]
    else:
        lines = [
            f"Hajmi: {engine_liters} litr" if engine_liters else "Hajmi: ma'lumot yo'q",
            f"Moy turi: {', '.join(engine_types)}" if engine_types else "Moy turi: ko'rsatilmagan",
            f"Almashtirish oralig'i: {config.SERVICE_INTERVALS['motor']}",
        ]
    stat_card(draw, 56, card_y, W - 112, 34 * len(lines) + 90, RED, "MOTOR MOYI", lines)
    y2 = card_y + 34 * len(lines) + 90 + 24

    gb_liters = car.get("gearbox_liters")
    gb_types = car.get("gearbox_oil_types") or []
    lines = [
        gearbox_kind or "Turi ko'rsatilmagan",
        f"Hajmi: {gb_liters} litr" if gb_liters else "Hajmi: ma'lumot yo'q",
        f"Moy turi: {', '.join(gb_types)}" if gb_types else "Moy turi: ko'rsatilmagan",
    ]
    if gb_liters:
        lines.append(f"Almashtirish oralig'i: {config.SERVICE_INTERVALS['gearbox']}")
    gb_h = 34 * len(lines) + 90
    red_liters = car.get("reductor_liters")

    if red_liters:
        stat_card(draw, 56, y2, card_w, gb_h, ACCENT, "KAROBKA", lines)
        red_types = car.get("reductor_oil_types") or []
        red_lines = [
            f"Hajmi: {red_liters} litr",
            f"Moy turi: {', '.join(red_types) if red_types else 'ko\'rsatilmagan'}",
            f"Almashtirish oralig'i: {config.SERVICE_INTERVALS['reductor']}",
        ]
        red_h = 34 * len(red_lines) + 90
        stat_card(draw, 56 + card_w + 24, y2, card_w, max(gb_h, red_h), GREEN, "REDUKTOR", red_lines)
    else:
        stat_card(draw, 56, y2, card_w, gb_h, ACCENT, "KAROBKA / TRANSMISSIYA", lines)

    footer_y = dynamic_h - 60
    draw.line([56, footer_y - 20, W - 56, footer_y - 20], fill=PANEL_BORDER, width=2)
    note = "Vektor-chizma texnik sxema — umumiy dvigatel tuzilmasi, aynan shu modelning haqiqiy tashqi ko'rinishi emas. Raqamlar Carland bazasidan."
    for i, line in enumerate(_wrap(draw, note, F_REG(19), W - 112)):
        draw.text((56, footer_y + i * 26), line, font=F_REG(19), fill=TEXT_MUTED)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()
