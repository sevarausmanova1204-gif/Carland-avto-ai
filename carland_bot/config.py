import os
from pathlib import Path
from dotenv import load_dotenv

# Avval joriy papkadagi .env, keyin yuqori papkadagi .env ni tekshirish
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"

load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

if not BOT_TOKEN:
    print("OGOHLANTIRISH: BOT_TOKEN topilmadi! Iltimos .env faylini to'ldiring.")

if not GEMINI_API_KEY:
    print("OGOHLANTIRISH: GEMINI_API_KEY topilmadi! AI javoblari uchun kalit zarur.")
