import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "data" / "carland.db"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").strip().lower()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

CARS_PER_PAGE = 8
PRODUCTS_PER_PAGE = 6

# Barcha mashinalar uchun standart almashtirish oralig'i (Carland xodimi
# tomonidan berilgan umumiy tavsiya — bazadagi har xil individual km
# qiymatlari o'rniga shu qo'llaniladi, chunki foydalanuvchi shunday so'radi).
SERVICE_INTERVALS = {
    "motor": "7 000 – 8 000 km",
    "gearbox": "35 000 – 40 000 km",
    "reductor": "15 000 – 20 000 km",
}

CATEGORY_LABELS = {
    "air": ("🌬 Havo filtri", "Air filters"),
    "oilf": ("🛢 Moy filtri", "Oils filters"),
    "cabin": ("❄️ Salon filtri", "Lounge filter"),
    "fuel": ("⛽ Yoqilg'i filtri", "Fuel filter"),
    "chem": ("🧴 Avtokimyo", "Autochemistry and autocosmetics"),
    "spare": ("⚙️ Ehtiyot qismlar", "SPARE PART"),
    "acc": ("🎒 Aksessuarlar", "Accessories"),
}

# Bu jadvallar alohida (products'dan boshqa) manbadan olinadi, yoki
# products ichida maxsus filtr bilan qidiriladi
SPECIAL_CATEGORIES = {
    "battery": "🔋 Akkumulyator",
    "antifreeze": "❄️ Antifriz",
    "spark": "🔌 Svecha",
    "tire": "🛞 Shina (balon)",
    "brake": "🔩 Tormoz kolodkalari",
}

# "Mahsulotlar" menyusida moylarni alohida (mashina tanlamasdan, davlat/brend
# kelib chiqishi bo'yicha) ko'rish uchun
OIL_BROWSE_CATEGORIES = {
    "motoroil": ("🛢 Motor moylari", ("Motor oils",)),
    "gearoil": ("⚙️ Transmissiya moylari", ("Transmission oils", "Transmission fluid")),
}

EUROPEAN_OIL_BRANDS = {
    "LIQUI MOLY", "SHELL", "CASTROL", "MOTUL", "ROWE", "ADDINOL", "DIVINOL",
    "FUCHS", "TOTAL", "FEBI", "MANNOL", "WIOLIN", "GRAUMANN", "VALESCO",
    "STARK", "AVENO", "ELF", "ARAL", "BP", "EUROL", "RAVENOL", "NESTE",
}

