"""Foydalanuvchi (Carland xodimi) tomonidan taqdim etilgan HAQIQIY mashina
rasmlari.

`assets/car_photos/` papkasiga qo'yilgan rasm faylining nomi (kengaytmasiz)
mashina modeliga mos kelishi kerak — katta-kichik harf, bo'sh joy va
tinish belgilaridagi farqlar muhim emas (masalan "Cobalt.jpg" yoki
"cobalt-avtomat.png" — "Cobalt (Avtomat)" modeliga ham mos keladi).

Agar biror mashina uchun bu yerda rasm topilsa, "🖼 Infografika" bo'limida
avtomatik chiziladigan SXEMATIK diagramma (bot/infographic.py) o'rniga
aynan shu haqiqiy rasm ko'rsatiladi (bot/handlers/callbacks.py da). Rasm
topilmagan mashinalar uchun avvalgidek avtomatik sxema davom etadi.
"""
import re
from pathlib import Path

PHOTOS_DIR = Path(__file__).resolve().parent.parent / "assets" / "car_photos"

_SUPPORTED_EXT = (".jpg", ".jpeg", ".png", ".webp")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def get_car_photo_path(model: str) -> Path | None:
    if not PHOTOS_DIR.exists():
        return None
    target = _slug(model)
    if not target:
        return None
    for path in sorted(PHOTOS_DIR.iterdir()):
        if path.suffix.lower() not in _SUPPORTED_EXT:
            continue
        if _slug(path.stem) == target:
            return path
    return None
