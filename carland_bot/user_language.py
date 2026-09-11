"""
Carland Telegram Bot - Foydalanuvchi Tili Boshqaruvi
O'zbekcha ('uz'), Ruscha ('ru'), Inglizcha ('en')
Sozlamalar JSON faylda avtomatik saqlanadi.
"""

import json
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

LANG_FILE = Path(__file__).parent / "user_languages.json"
_USER_LANGS: Dict[int, str] = {}


def _load_languages():
    """Fayldan tillarni yuklash"""
    global _USER_LANGS
    if LANG_FILE.exists():
        try:
            with open(LANG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                _USER_LANGS = {int(k): str(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Foydalanuvchi tillarini yuklashda xatolik: {e}")
            _USER_LANGS = {}


def _save_languages():
    """Tillarni faylga saqlash"""
    try:
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            json.dump(_USER_LANGS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Foydalanuvchi tillarini saqlashda xatolik: {e}")


# Dastur ishga tushganda yuklash
_load_languages()


def get_user_lang(user_id: int) -> str:
    """Foydalanuvchi tanlagan tilni olish (Standart: 'uz')"""
    return _USER_LANGS.get(user_id, "uz")


def has_user_lang(user_id: int) -> bool:
    """Foydalanuvchi avval til tanlaganmi?"""
    return user_id in _USER_LANGS


def set_user_lang(user_id: int, lang: str):
    """Foydalanuvchi tilini saqlash ('uz', 'ru', 'en')"""
    if lang not in ["uz", "ru", "en"]:
        lang = "uz"
    _USER_LANGS[user_id] = lang
    _save_languages()
