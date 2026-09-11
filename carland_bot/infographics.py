"""
Carland Telegram Bot - Avtomobillar Infografika Generator Moduli
Barcha bazadagi mashinalarning matori, karobkasi, reduktori va filtrlari (moy, havo, salon)
uchun zamonaviy, brendlangan 1200x800 yuqori sifatli infografika kartalarini 0.05 soniyada tayyorlaydi.
"""

import os
from io import BytesIO
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

# Shriftlar
FONT_DIR = "/System/Library/Fonts/Supplemental"
BOLD_FONT_PATH = os.path.join(FONT_DIR, "Arial Bold.ttf")
REGULAR_FONT_PATH = os.path.join(FONT_DIR, "Arial.ttf")

if not os.path.exists(BOLD_FONT_PATH):
    BOLD_FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"
if not os.path.exists(REGULAR_FONT_PATH):
    REGULAR_FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"

def get_font(size: int, bold: bool = False):
    try:
        path = BOLD_FONT_PATH if bold else REGULAR_FONT_PATH
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Ranglar palitrasi (Carland Dark Theme)
BG_TOP = (11, 19, 43)        # #0B132B (Deep Space Navy)
BG_BOTTOM = (28, 37, 65)     # #1C2541
CARD_BORDER = (46, 64, 102)  # Card border
ACCENT_CYAN = (0, 245, 212)   # #00F5D4 (Vibrant Cyan)
ACCENT_GOLD = (255, 183, 3)   # #FFB703 (Carland Amber/Gold)
ACCENT_RED = (239, 71, 111)   # #EF476F (Carland Red)
TEXT_WHITE = (255, 255, 255)
TEXT_GRAY = (175, 190, 215)
TEXT_MUTED = (120, 138, 168)

def draw_gradient(draw: ImageDraw.ImageDraw, width: int, height: int):
    """Orqa fon gradientini chizish"""
    for y in range(height):
        ratio = y / height
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def draw_rounded_card(draw: ImageDraw.ImageDraw, box, radius=16, fill=(20, 32, 58), outline=CARD_BORDER, width=2):
    """Burchaklari yumaloqlangan karta chizish"""
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# Avtomobillarning haqiqiy 3D anatomik mator va uzatmalar qutisi infografikalari
REAL_ENGINE_ASSETS = {
    "cobalt": "assets/infographics/cobalt_engine.jpg",
    "gentra": "assets/infographics/gentra_engine.jpg",
    "lacetti": "assets/infographics/lacetti_engine.jpg",
    "nexia_3": "assets/infographics/nexia_3_engine.jpg",
    "nexia": "assets/infographics/nexia_3_engine.jpg",
    "tracker": "assets/infographics/tracker_engine.jpg",
    "onix": "assets/infographics/onix_engine.jpg",
    "monza": "assets/infographics/monza_engine.jpg",
    "id4": "assets/infographics/id4_engine.jpg",
    "id6": "assets/infographics/id6_engine.jpg",
    "eq7": "assets/infographics/eq7_engine.jpg",
    "song": "assets/infographics/song_engine.jpg",
    "chazor": "assets/infographics/chazor_engine.jpg",
    "yuan_up": "assets/infographics/yuan_up_engine.jpg",
    "deepal": "assets/infographics/deepal_engine.jpg"
}


def get_real_engine_infographic(car_name: str, info_type: str = "mator") -> Optional[BytesIO]:
    """
    Agar mashinaning haqiqiy 3D mator/uzatmalar qutisi infografikasi mavjud bo'lsa,
    uni yuqori sifatda BytesIO ko'rinishida qaytaradi.
    """
    c_lower = car_name.lower()
    matched_key = None
    for k in REAL_ENGINE_ASSETS:
        if k in c_lower or k.replace("_", " ") in c_lower:
            matched_key = k
            break
            
    if not matched_key:
        if "id.4" in c_lower or "id 4" in c_lower:
            matched_key = "id4"
        elif "id.6" in c_lower or "id 6" in c_lower:
            matched_key = "id6"
        elif "byd" in c_lower:
            matched_key = "song"
            
    if matched_key and matched_key in REAL_ENGINE_ASSETS:
        path = REAL_ENGINE_ASSETS[matched_key]
        if os.path.exists(path):
            with open(path, "rb") as f:
                bio = BytesIO(f.read())
                bio.seek(0)
                return bio
    return None


def generate_vehicle_infographic(car: Dict[str, Any], info_type: str = "umumiy", lang: str = "uz") -> BytesIO:
    """
    Avtomobil uchun infografika tasvirini yaratish
    info_type: 'mator', 'karobka', 'reduktor', 'filtrlar', 'umumiy'
    """
    # 0. Haqiqiy 3D mator va uzatmalar qutisi infografikasi mavjud bo'lsa
    if info_type in ["mator", "karobka", "reduktor", "umumiy"]:
        real_bio = get_real_engine_infographic(car.get("name", ""), info_type=info_type)
        if real_bio:
            return real_bio

    WIDTH = 1200
    HEIGHT = 800
    
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_TOP)
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, WIDTH, HEIGHT)
    
    # 1. HEADER (Carland Brand)
    draw.rectangle([(0, 0), (WIDTH, 90)], fill=(8, 14, 30))
    draw.line([(0, 90), (WIDTH, 90)], fill=ACCENT_GOLD, width=3)
    
    # Header logo va matn
    font_logo = get_font(28, bold=True)
    font_sublogo = get_font(15, bold=False)
    draw.text((40, 22), "CARLAND", font=font_logo, fill=ACCENT_GOLD)
    draw.text((170, 22), "AUTO SERVICE", font=font_logo, fill=TEXT_WHITE)
    draw.text((40, 58), "AVTO MOYLAR VA SERVIS MARKAZI | 15 TA FILIAL", font=font_sublogo, fill=TEXT_GRAY)
    
    # O'ng tomonda Call Center
    font_call = get_font(20, bold=True)
    draw.text((WIDTH - 300, 30), "CALL-CENTER: 55 516 16 16", font=font_call, fill=ACCENT_CYAN)
    
    # 2. SUB-HEADER: Turi va Avtomobil nomi
    car_name = car.get("name", "Avtomobil").upper()
    brand_name = car.get("brand", "").upper()
    
    type_titles = {
        "mator": ("DVIGATEL (MATOR) MOYI ME'YORI", ACCENT_GOLD),
        "karobka": ("UZATMALAR QUTISI (KAROBKA) MOYI", ACCENT_CYAN),
        "reduktor": ("REDUKTOR MOYI (EV & GIBRID)", ACCENT_CYAN),
        "filtrlar": ("FILTRLAR (MOY, HAVO, SALON)", ACCENT_GOLD),
        "umumiy": ("TO'LIQ TEXNIK PASPORT & ME'YORLAR", ACCENT_GOLD)
    }
    type_title, badge_color = type_titles.get(info_type, ("TEXNIK ME'YORLAR", ACCENT_GOLD))
    
    # Badge
    draw_rounded_card(draw, [(40, 110), (WIDTH - 40, 190)], radius=12, fill=(15, 24, 45), outline=badge_color, width=2)
    font_badge = get_font(16, bold=True)
    font_car = get_font(30, bold=True)
    
    draw.text((60, 120), f"RUSUMI: {brand_name} | {type_title}", font=font_badge, fill=badge_color)
    draw.text((60, 145), car_name, font=font_car, fill=TEXT_WHITE)
    
    # 3. ASOSIY BLOKLAR (info_type ga qarab)
    font_h1 = get_font(22, bold=True)
    font_val = get_font(26, bold=True)
    font_p = get_font(18, bold=False)
    font_p_bold = get_font(18, bold=True)
    
    if info_type == "mator":
        # MATOR INFOGRAFIKASI
        draw_rounded_card(draw, [(40, 210), (580, 520)], radius=16, fill=(16, 26, 50), outline=CARD_BORDER)
        draw.text((70, 235), "DVIGATEL MOY SIG'IMI", font=font_h1, fill=ACCENT_CYAN)
        draw.text((70, 275), car.get("engine_oil", "-"), font=font_val, fill=TEXT_WHITE)
        
        draw.text((70, 340), "TAVSIYA ETILADIGAN QOVUSHQOQLIK", font=font_h1, fill=ACCENT_CYAN)
        draw.text((70, 380), car.get("engine_oil_type", "0W-20 / 5W-30"), font=font_val, fill=ACCENT_GOLD)
        
        oil_filt = car.get("oil_filter", "Standart OEM / OP 570")
        draw.text((70, 445), f"• Moy filtri: {oil_filt}", font=font_p_bold, fill=TEXT_WHITE)
        draw.text((70, 475), f"• Almashtirish oralig'i: {car.get('filter_interval', '20 000 km')}", font=font_p, fill=TEXT_GRAY)
        
        # O'ng karta: Carland afzalliklari va Moy brendlari
        draw_rounded_card(draw, [(620, 210), (1160, 520)], radius=16, fill=(16, 26, 50), outline=ACCENT_GOLD)
        draw.text((650, 235), "CARLAND SIFAT STANDARTLARI", font=font_h1, fill=ACCENT_GOLD)
        
        lines = [
            "• Shell Ultra AG 5W-30 (Germaniya) — 110 000 so'm/L",
            "• Castrol Magnatec / Edge 5W-30 / 5W-40 — 140 000 so'm/L",
            "• Liqui Moly Molygen / Top Tec 5W-30 — 160 000 so'm/L",
            "• Valvoline SynPower 0W-20 / 5W-30 (DEXOS) — 170 000 so'm/L",
        ]
        y_pos = 285
        for l in lines:
            draw.text((650, y_pos), l, font=font_p, fill=TEXT_WHITE)
            y_pos += 42
            
        # Super Banner: Bepul almashtirish
        draw_rounded_card(draw, [(40, 540), (1160, 680)], radius=14, fill=(20, 45, 30), outline=(46, 196, 182), width=2)
        font_big_alert = get_font(24, bold=True)
        draw.text((70, 565), "CARLAND SERVISLARIDA MATOR MOYI ALMASHTIRISH MUTLAQO BEPUL!", font=font_big_alert, fill=(46, 196, 182))
        font_alert_sub = get_font(18, bold=False)
        draw.text((70, 605), "• Carland do'konidan dvigatel moyi xarid qilinganda almashtirish xizmati bepul amalga oshiriladi.", font=font_alert_sub, fill=TEXT_WHITE)
        draw.text((70, 635), "• Eslatma: Bepul almashtirish faqatgina dvigatel moyi uchun amal qiladi.", font=font_alert_sub, fill=TEXT_GRAY)

    elif info_type == "karobka":
        # KAROBKA INFOGRAFIKASI
        draw_rounded_card(draw, [(40, 210), (580, 520)], radius=16, fill=(16, 26, 50), outline=CARD_BORDER)
        draw.text((70, 235), "UZATMALAR QUTISI (KAROBKA)", font=font_h1, fill=ACCENT_CYAN)
        
        g_oil = car.get("gearbox_oil", "-")
        draw.text((70, 280), "Moy hajmi:", font=font_p, fill=TEXT_GRAY)
        draw.text((70, 310), g_oil[:35], font=font_val, fill=TEXT_WHITE)
        
        g_type = car.get("gearbox_oil_type", "-")
        draw.text((70, 370), "Tavsiya etiladigan moy turi:", font=font_p, fill=TEXT_GRAY)
        draw.text((70, 400), g_type, font=font_val, fill=ACCENT_GOLD)
        draw.text((70, 465), "Avtomat (AKPP) / Mexanika (MKPP)", font=font_p_bold, fill=ACCENT_CYAN)
        
        # O'ng karta: Apparatda to'liq yuvish aksiyasi
        draw_rounded_card(draw, [(620, 210), (1160, 520)], radius=16, fill=(16, 26, 50), outline=ACCENT_CYAN)
        draw.text((650, 235), "APPARATDA TO'LIQ ALMASHTIRISH", font=font_h1, fill=ACCENT_CYAN)
        
        draw.text((650, 285), "SENTABR OYI AKSIYASI:", font=font_p_bold, fill=ACCENT_GOLD)
        draw.text((650, 320), "Avtomat karobka moyini maxsus apparatda", font=font_p, fill=TEXT_WHITE)
        draw.text((650, 355), "100% to'liq yuvish va almashtirish — 720 000 so'm!", font=font_val, fill=ACCENT_GOLD)
        
        draw.text((650, 420), "• Tizimdagi eski qoldiqlarni to'liq tozalaydi", font=font_p, fill=TEXT_GRAY)
        draw.text((650, 455), "• Uzatmalar qutisi umrini 2 baravarga uzaytiradi", font=font_p, fill=TEXT_GRAY)
        
        # Eslatma banner
        draw_rounded_card(draw, [(40, 540), (1160, 680)], radius=14, fill=(35, 25, 20), outline=ACCENT_GOLD, width=2)
        draw.text((70, 570), "KAROBKA VA REDUKTOR MOYI XIZMAT HAQI", font=get_font(22, bold=True), fill=ACCENT_GOLD)
        draw.text((70, 610), "Karobka va reduktor moyini alishtirishda mashina rusumiga qarab xizmat haqi olinadi.", font=font_p, fill=TEXT_WHITE)
        draw.text((70, 640), "Aniq narx va maslahat olish uchun: +998 55 516 16 16", font=font_p_bold, fill=ACCENT_CYAN)

    elif info_type == "reduktor":
        # REDUKTOR INFOGRAFIKASI
        draw_rounded_card(draw, [(40, 210), (580, 520)], radius=16, fill=(16, 26, 50), outline=CARD_BORDER)
        draw.text((70, 235), "REDUKTOR MOY SIG'IMI VA TURI", font=font_h1, fill=ACCENT_CYAN)
        
        red_oil = car.get("reductor_oil", "-")
        draw.text((70, 280), "Hajmi va turi:", font=font_p, fill=TEXT_GRAY)
        draw.text((70, 315), red_oil, font=get_font(24, bold=True), fill=ACCENT_GOLD)
        
        draw.text((70, 390), f"Filtr/Moy oralig'i: {car.get('filter_interval', '30 000 km')}", font=font_p_bold, fill=TEXT_WHITE)
        notes = car.get("notes", "To'liq elektr yoki gibrid texnologiyasi")
        draw.text((70, 435), f"Qayd: {notes[:60]}", font=font_p, fill=TEXT_GRAY)
        
        # O'ng karta: EV & Gibrid talablari
        draw_rounded_card(draw, [(620, 210), (1160, 520)], radius=16, fill=(16, 26, 50), outline=ACCENT_CYAN)
        draw.text((650, 235), "MAXSUS DIELEKTRIK EV MOYLAR", font=font_h1, fill=ACCENT_CYAN)
        
        lines_red = [
            "• Elektromobillar (EV) yuqori aylanishlar tezligida ishlaydi;",
            "• Maxsus EV / D1 / D2 reduktor moylari elektr tokini o'tkazmaydi;",
            "• Reduktordagi tishli g'ildiraklarni yeyilishdan asraydi;",
            "• O'z vaqtida almashtirish motor quvvatini tejaydi."
        ]
        y_r = 285
        for lr in lines_red:
            draw.text((650, y_r), lr, font=font_p, fill=TEXT_WHITE)
            y_r += 42
            
        # Banner
        draw_rounded_card(draw, [(40, 540), (1160, 680)], radius=14, fill=(15, 30, 45), outline=ACCENT_CYAN, width=2)
        draw.text((70, 570), "CARLAND ELEKTROMOBIL VA GIBRID SERVISI", font=get_font(22, bold=True), fill=ACCENT_CYAN)
        draw.text((70, 610), "Barcha 15 ta filialimizda professional apparat va sifatli moylar kafolatlanadi.", font=font_p, fill=TEXT_WHITE)
        draw.text((70, 640), "Xizmat haqi mashina modeliga qarab belgilanadi | Call-center: +998 55 516 16 16", font=font_p, fill=TEXT_GRAY)

    elif info_type == "filtrlar":
        # FILTRLAR INFOGRAFIKASI (Moy filtri, Havo filtri, Salon filtri)
        card_w = 350
        # 1. Moy filtri
        draw_rounded_card(draw, [(40, 210), (40 + card_w, 520)], radius=16, fill=(16, 26, 50), outline=ACCENT_GOLD)
        draw.text((65, 235), "MOY FILTRI", font=font_h1, fill=ACCENT_GOLD)
        oil_f = car.get("oil_filter", "Standart OEM / OP 570")
        draw.text((65, 280), "Model kodi:", font=font_p, fill=TEXT_GRAY)
        draw.text((65, 310), oil_f, font=get_font(24, bold=True), fill=TEXT_WHITE)
        draw.text((65, 370), "Almashtirish oralig'i:", font=font_p, fill=TEXT_GRAY)
        draw.text((65, 400), "Har 8 000 - 10 000 km", font=font_p_bold, fill=ACCENT_CYAN)
        draw.text((65, 440), "Dvigatel moyi bilan birga\nalmashtirish shart!", font=font_p, fill=TEXT_GRAY)
        
        # 2. Havo (vazdushniy) filtri
        draw_rounded_card(draw, [(425, 210), (425 + card_w, 520)], radius=16, fill=(16, 26, 50), outline=ACCENT_CYAN)
        draw.text((450, 235), "HAVO (VAZDUSHNIY)", font=font_h1, fill=ACCENT_CYAN)
        draw.text((450, 280), "Dvigatel havosi:", font=font_p, fill=TEXT_GRAY)
        draw.text((450, 310), "Yuqori oqimli filtr", font=get_font(24, bold=True), fill=TEXT_WHITE)
        draw.text((450, 370), "Almashtirish oralig'i:", font=font_p, fill=TEXT_GRAY)
        draw.text((450, 400), "Har 10 000 km", font=font_p_bold, fill=ACCENT_GOLD)
        draw.text((450, 440), "Matorga toza havo beradi,\nyonilg'i sarfini kamaytiradi.", font=font_p, fill=TEXT_GRAY)
        
        # 3. Salon filtri
        draw_rounded_card(draw, [(810, 210), (810 + card_w, 520)], radius=16, fill=(16, 26, 50), outline=(130, 200, 255))
        draw.text((835, 235), "SALON FILTRI", font=font_h1, fill=(130, 200, 255))
        draw.text((835, 280), "Konditsioner/Salon:", font=font_p, fill=TEXT_GRAY)
        draw.text((835, 310), "Ko'mirli (Anti-allergen)", font=get_font(22, bold=True), fill=TEXT_WHITE)
        draw.text((835, 370), "Almashtirish oralig'i:", font=font_p, fill=TEXT_GRAY)
        draw.text((835, 400), "Har 10 000 - 15 000 km", font=font_p_bold, fill=ACCENT_CYAN)
        draw.text((835, 440), "Salon havosini chang,\nhid va allergenlardan tozalaydi.", font=font_p, fill=TEXT_GRAY)
        
        # Banner
        draw_rounded_card(draw, [(40, 540), (1160, 680)], radius=14, fill=(20, 35, 45), outline=ACCENT_GOLD, width=2)
        draw.text((70, 570), "ASL VA SIFATLI FILTRLAR CARLAND FILIALLARIDA MAVJUD", font=get_font(22, bold=True), fill=ACCENT_GOLD)
        draw.text((70, 610), "Mutaxassislarimiz filtr holatini bepul tekshirib beradi va yangisiga almashtiradi.", font=font_p, fill=TEXT_WHITE)
        draw.text((70, 640), "Call-center: +998 55 516 16 16 | Onlayn navbat: carland.uz", font=font_p_bold, fill=ACCENT_CYAN)

    else:
        # UMUMIY KOMPLEKS INFOGRAFIKA (4 TA BLOK)
        # Blok 1: Mator
        draw_rounded_card(draw, [(40, 210), (580, 360)], radius=14, fill=(16, 26, 50), outline=ACCENT_GOLD)
        draw.text((65, 225), "DVIGATEL (MATOR) MOYI", font=font_h1, fill=ACCENT_GOLD)
        draw.text((65, 265), f"Hajmi: {car.get('engine_oil', '-')}", font=font_p_bold, fill=TEXT_WHITE)
        draw.text((65, 300), f"Turi: {car.get('engine_oil_type', '-')}", font=font_p, fill=ACCENT_CYAN)
        draw.text((380, 265), f"Moy filtri: {car.get('oil_filter', 'OEM')}", font=font_p, fill=TEXT_GRAY)
        draw.text((380, 300), "Bepul almashtirish!", font=font_p_bold, fill=(46, 196, 182))
        
        # Blok 2: Karobka
        draw_rounded_card(draw, [(620, 210), (1160, 360)], radius=14, fill=(16, 26, 50), outline=ACCENT_CYAN)
        draw.text((645, 225), "UZATMALAR QUTISI (KAROBKA)", font=font_h1, fill=ACCENT_CYAN)
        draw.text((645, 265), f"Hajmi: {car.get('gearbox_oil', '-')[:32]}", font=font_p_bold, fill=TEXT_WHITE)
        draw.text((645, 300), f"Turi: {car.get('gearbox_oil_type', '-')}", font=font_p, fill=ACCENT_GOLD)
        
        # Blok 3: Reduktor
        draw_rounded_card(draw, [(40, 380), (580, 530)], radius=14, fill=(16, 26, 50), outline=CARD_BORDER)
        draw.text((65, 395), "REDUKTOR MOYI", font=font_h1, fill=ACCENT_CYAN)
        draw.text((65, 435), f"Hajmi va turi: {car.get('reductor_oil', '-')}", font=font_p_bold, fill=TEXT_WHITE)
        draw.text((65, 470), "Maxsus EV/Gibrid yoki mexanik moy", font=font_p, fill=TEXT_GRAY)
        
        # Blok 4: Filtrlar
        draw_rounded_card(draw, [(620, 380), (1160, 530)], radius=14, fill=(16, 26, 50), outline=CARD_BORDER)
        draw.text((645, 395), "FILTRLAR VA XIZMAT ORALIG'I", font=font_h1, fill=ACCENT_GOLD)
        draw.text((645, 435), f"Moy filtri: {car.get('oil_filter', 'Standart OEM')} | Havo | Salon", font=font_p_bold, fill=TEXT_WHITE)
        draw.text((645, 470), f"Filtr oralig'i: {car.get('filter_interval', '20 000 km')}", font=font_p, fill=ACCENT_CYAN)
        
        # Banner
        draw_rounded_card(draw, [(40, 550), (1160, 680)], radius=14, fill=(15, 25, 40), outline=ACCENT_GOLD, width=2)
        draw.text((70, 575), "CARLAND SERVISLARIDA MATOR MOYI ALMASHTIRISH MUTLAQO BEPUL!", font=get_font(22, bold=True), fill=(46, 196, 182))
        draw.text((70, 615), "Karobka va reduktor moyini alishtirishda mashina rusumiga qarab xizmat haqi olinadi.", font=font_p, fill=TEXT_WHITE)
        draw.text((70, 645), "Ish vaqti: 09:00 - 23:00 dam olish kunlarisiz | Call-center: +998 55 516 16 16", font=font_p_bold, fill=ACCENT_CYAN)

    # 4. FOOTER
    draw.rectangle([(0, 710), (WIDTH, HEIGHT)], fill=(8, 14, 30))
    draw.line([(0, 710), (WIDTH, 710)], fill=CARD_BORDER, width=2)
    
    font_footer = get_font(16, bold=False)
    font_footer_bold = get_font(16, bold=True)
    draw.text((40, 735), "15 TA FILIAL: Toshkent, Samarqand, Buxoro, Qarshi, Chirchiq, Olmaliq", font=font_footer, fill=TEXT_GRAY)
    draw.text((WIDTH - 250, 735), "WWW.CARLAND.UZ", font=font_footer_bold, fill=ACCENT_GOLD)
    draw.text((WIDTH - 480, 735), "ISH VAQTI: 09:00 - 23:00", font=font_footer, fill=TEXT_WHITE)
    
    # Baytlar oqimiga saqlash (PNG format)
    bio = BytesIO()
    bio.name = f"{car.get('name', 'car')}_{info_type}.png"
    img.save(bio, format="PNG", optimize=True)
    bio.seek(0)
    return bio
