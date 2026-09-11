import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylidan o'zgaruvchilarni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# Yuklab olinadigan vaqtinchalik videolar papkasi
BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Maksimal fayl hajmi (Telegram Bot API limiti odatda 50MB)
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
