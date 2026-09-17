import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "data" / "carland.db"

# Foydalanuvchi sozlamalari (til, oxirgi tanlangan mashina va h.k.) shu
# papkaga saqlanadi. MUHIM: bu "data/" papkasidan ATAYLAB alohida — "data/"
# git repozitoriyga tegishli (carland.db shu yerda, git push orqali
# yangilanadi), agar foydalanuvchi sozlamalari ham o'sha papkaga yozilsa,
# keyingi git-deploy paytida ular carland.db bilan birga qayta yozilib
# ketishi yoki, aksincha, git-committed carland.db'ni eskirtirib qo'yishi
# mumkin edi. Shu sababli Railway'da bu papka alohida persistent volume'ga
# ulanadi (PERSIST_DIR muhit o'zgaruvchisi orqali) — shunda bot qayta
# deploy/restart bo'lganda ham foydalanuvchining til tanlovi va h.k.
# YO'QOLMAYDI (avval har bir deploy'da hammaning tili "uz"ga qaytib
# ketardi, chunki bular faqat operativ xotirada — context.user_data'da —
# saqlanardi).
PERSIST_DIR = Path(os.getenv("PERSIST_DIR", str(BASE_DIR / "persist")))
PERSIST_DIR.mkdir(parents=True, exist_ok=True)
PERSISTENCE_PATH = PERSIST_DIR / "bot_persistence.pickle"

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
SERVICE_INTERVALS_RU = {
    "motor": "7 000 – 8 000 км",
    "gearbox": "35 000 – 40 000 км",
    "reductor": "15 000 – 20 000 км",
}


def service_interval_ru(part: str) -> str:
    return SERVICE_INTERVALS_RU.get(part, SERVICE_INTERVALS.get(part, ""))


# Har bir yozuv: (slug -> {"uz": ..., "ru": ..., "category": bazadagi haqiqiy
# category nomi}). "category" ustuni tarjima QILINMAYDI — bu SQL so'rovda
# ishlatiladigan haqiqiy ustun qiymati (products.category), faqat "uz"/"ru"
# ko'rsatiladigan tugma matnidir.
CATEGORY_LABELS = {
    "air": {"uz": "🌬 Havo filtri", "ru": "🌬 Воздушный фильтр", "category": "Air filters"},
    "oilf": {"uz": "🛢 Moy filtri", "ru": "🛢 Масляный фильтр", "category": "Oils filters"},
    "cabin": {"uz": "❄️ Salon filtri", "ru": "❄️ Салонный фильтр", "category": "Lounge filter"},
    "fuel": {"uz": "⛽ Yoqilg'i filtri", "ru": "⛽ Топливный фильтр", "category": "Fuel filter"},
    "chem": {"uz": "🧴 Avtokimyo", "ru": "🧴 Автохимия", "category": "Autochemistry and autocosmetics"},
    "spare": {"uz": "⚙️ Ehtiyot qismlar", "ru": "⚙️ Запчасти", "category": "SPARE PART"},
    "acc": {"uz": "🎒 Aksessuarlar", "ru": "🎒 Аксессуары", "category": "Accessories"},
}

# Bu jadvallar alohida (products'dan boshqa) manbadan olinadi, yoki
# products ichida maxsus filtr bilan qidiriladi
SPECIAL_CATEGORIES = {
    "battery": {"uz": "🔋 Akkumulyator", "ru": "🔋 Аккумулятор"},
    "antifreeze": {"uz": "❄️ Antifriz", "ru": "❄️ Антифриз"},
    "spark": {"uz": "🔌 Svecha", "ru": "🔌 Свечи"},
    "tire": {"uz": "🛞 Shina (balon)", "ru": "🛞 Шины"},
    "brake": {"uz": "🔩 Tormoz kolodkalari", "ru": "🔩 Тормозные колодки"},
}

# "Mahsulotlar" menyusida moylarni alohida (mashina tanlamasdan, davlat/brend
# kelib chiqishi bo'yicha) ko'rish uchun
OIL_BROWSE_CATEGORIES = {
    "motoroil": {"uz": "🛢 Motor moylari", "ru": "🛢 Моторные масла", "cats": ("Motor oils",)},
    "gearoil": {
        "uz": "⚙️ Transmissiya moylari",
        "ru": "⚙️ Трансмиссионные масла",
        "cats": ("Transmission oils", "Transmission fluid"),
    },
}


def category_label(slug: str, lang: str = "uz") -> str:
    entry = CATEGORY_LABELS.get(slug, {})
    return entry.get(lang, entry.get("uz", slug))


def special_category_label(slug: str, lang: str = "uz") -> str:
    entry = SPECIAL_CATEGORIES.get(slug, {})
    return entry.get(lang, entry.get("uz", slug))


def oil_browse_label(slug: str, lang: str = "uz") -> str:
    entry = OIL_BROWSE_CATEGORIES.get(slug, {})
    return entry.get(lang, entry.get("uz", slug))


def category_db(slug: str) -> str:
    """products.category ustunidagi HAQIQIY (tarjima qilinmaydigan) qiymat."""
    return CATEGORY_LABELS.get(slug, {}).get("category", "")


def oil_browse_cats(slug: str) -> tuple:
    """Haqiqiy (tarjima qilinmaydigan) products.category qiymatlari to'plami."""
    return OIL_BROWSE_CATEGORIES.get(slug, {}).get("cats", ())


# Karobka/reduktor moyi hisoblanganda har doim ko'rsatiladigan eslatma —
# aniq mashina toifasiga bog'lamasdan, uchala narx oralig'ini ham ko'rsatib,
# xodim bilan filialda aniqlashtirishni so'raydi (foydalanuvchi so'rovi
# bo'yicha: har doim eslatma tarzida, barcha uchta summa bilan).
SERVICE_FEE_NOTE = (
    "🔧 *Xizmat haqqi* (o'rnatish/almashtirish uslugasi, moy narxiga kirmaydi): "
    "mashina turiga qarab 150 000 / 200 000 / 300 000 so'm. Aniq summani filialda so'rang."
)
SERVICE_FEE_NOTE_RU = (
    "🔧 *Стоимость услуги* (установка/замена, не включает цену масла): "
    "150 000 / 200 000 / 300 000 сум в зависимости от типа автомобиля. Точную сумму уточните в филиале."
)


def service_fee_note(lang: str = "uz") -> str:
    return SERVICE_FEE_NOTE_RU if lang == "ru" else SERVICE_FEE_NOTE

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

