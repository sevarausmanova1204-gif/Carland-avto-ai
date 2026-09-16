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

# Karobka/reduktor moyi hisoblanganda har doim ko'rsatiladigan eslatma —
# aniq mashina toifasiga bog'lamasdan, uchala narx oralig'ini ham ko'rsatib,
# xodim bilan filialda aniqlashtirishni so'raydi (foydalanuvchi so'rovi
# bo'yicha: har doim eslatma tarzida, barcha uchta summa bilan).
SERVICE_FEE_NOTE = (
    "🔧 *Xizmat haqqi* (o'rnatish/almashtirish uslugasi, moy narxiga kirmaydi): "
    "mashina turiga qarab 150 000 / 200 000 / 300 000 so'm. Aniq summani filialda so'rang."
)

EUROPEAN_OIL_BRANDS = {
    "LIQUI MOLY", "SHELL", "CASTROL", "MOTUL", "ROWE", "ADDINOL", "DIVINOL",
    "FUCHS", "TOTAL", "FEBI", "MANNOL", "WIOLIN", "GRAUMANN", "VALESCO",
    "STARK", "AVENO", "ELF", "ARAL", "BP", "EUROL", "RAVENOL", "NESTE",
}

# Foydalanuvchi (Carland xo'jayini) aniq talabi bo'yicha: Valvoline brendiga
# doim ko'proq urg'u berilishi kerak — har bir qism (motor/karobka/reduktor)
# uchun narx ro'yxati ko'rsatilganda, agar shu brendning mos mahsuloti
# mavjud bo'lsa, u albatta "🔴 Premium" segmentida ko'rinib turishi lozim
# (ro'yxat uzun bo'lgani uchun kesib tashlanib qolmasligi kerak).
PRIORITY_BRANDS = {"VALVOLINE"}

