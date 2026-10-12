"""Foydalanuvchi (Carland xodimi) tomonidan taqdim etilgan HAQIQIY mashina
rasmlari.

`assets/car_photos/` papkasiga qo'yilgan rasm faylining nomi (kengaytmasiz)
mashina modeliga mos kelishi kerak — katta-kichik harf, bo'sh joy va
tinish belgilaridagi farqlar muhim emas (masalan "Cobalt.jpg" yoki
"cobalt-avtomat.png" — "Cobalt (Avtomat)" modeliga ham mos keladi).

Bitta mashina rusumi uchun bir nechta rasm (masalan turli dvigatel
hajmlari) bo'lishi mumkin — buning uchun fayl nomiga "__" va ixtiyoriy
belgi qo'shiladi: "Malibu 2__1.jpg", "Malibu 2__2.jpg". Bunday fayllarning
hammasi fayl nomi tartibida birga yuboriladi.

Agar biror mashina uchun bu yerda rasm topilsa, "🖼 Infografika" bo'limida
avtomatik chiziladigan SXEMATIK diagramma (bot/infographic.py) o'rniga
aynan shu haqiqiy rasm(lar) ko'rsatiladi (bot/handlers/callbacks.py da).
Rasm topilmagan mashinalar uchun avvalgidek avtomatik sxema davom etadi.
"""
import re
from pathlib import Path

PHOTOS_DIR = Path(__file__).resolve().parent.parent / "assets" / "car_photos"

_SUPPORTED_EXT = (".jpg", ".jpeg", ".png", ".webp")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def get_car_photo_paths(model: str) -> list[Path]:
    if not PHOTOS_DIR.exists():
        return []
    target = _slug(model)
    if not target:
        return []
    found = []
    for path in sorted(PHOTOS_DIR.iterdir()):
        if path.suffix.lower() not in _SUPPORTED_EXT:
            continue
        if _slug(path.stem.split("__", 1)[0]) == target:
            found.append(path)
    return found
