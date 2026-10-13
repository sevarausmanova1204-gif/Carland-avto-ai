"""Mashina rusumini avtomobil markasiga (brendiga) ajratish.

Baza jadvalida marka nomi har doim ham model nomida yozilmagan — masalan
GM/Chevrolet oilaviy modellar (Cobalt, Nexia, Captiva, Malibu...) faqat
o'zining nomi bilan saqlangan, marka ko'rsatilmagan. Shu sababli bunday
modellar uchun qo'lda tuzilgan ro'yxat orqali "Chevrolet" markasi biriktiriladi.
"""
import json
import re
from pathlib import Path

from . import db

_BRANDS_JSON = Path(__file__).resolve().parent.parent / "data" / "car_brands.json"

CHEVROLET_MODELS = {
    "captiva", "cobalt", "damas", "equinox", "gentra", "labo", "lacetti",
    "malibu", "matiz", "nexia", "tahoe", "tracker", "traverse", "onix",
    "trailblazer", "spark",
}

BRAND_PREFIXES = [
    ("byd", "BYD"),
    ("kia", "Kia"),
    ("hyundai", "Hyundai"),
    ("chery", "Chery"),
    ("changan", "Changan (Deepal)"),
    ("deepal", "Changan (Deepal)"),
    ("haval", "Haval"),
    ("jetour", "Jetour"),
    ("zeekr", "Zeekr"),
    ("leapmotor", "Leapmotor"),
    ("dongfeng", "Dongfeng"),
    ("voyah", "Voyah"),
    ("gac", "GAC"),
    ("volkswagen", "Volkswagen"),
]

# Tugmalar shu tartibda chiqadi (skrinshotdagi ko'rinishga mos)
BRAND_ORDER = [
    "chevrolet", "kia", "hyundai", "byd", "chery", "changan", "haval",
    "jetour", "zeekr", "leapmotor", "dongfeng", "voyah", "gac",
    "volkswagen", "other",
]

BRAND_LABELS = {
    "chevrolet": "Chevrolet",
    "kia": "Kia",
    "hyundai": "Hyundai",
    "byd": "BYD",
    "chery": "Chery",
    "changan": "Changan (Deepal)",
    "haval": "Haval",
    "jetour": "Jetour",
    "zeekr": "Zeekr",
    "leapmotor": "Leapmotor",
    "dongfeng": "Dongfeng",
    "voyah": "Voyah",
    "gac": "GAC",
    "volkswagen": "Volkswagen",
    "other": "Boshqalar",
}


def slugify_brand(label: str) -> str:
    for slug, lbl in BRAND_PREFIXES:
        if lbl == label:
            return slug
    return "other"


_car_brand_map: dict | None = None


def car_brand_label(model: str) -> str:
    """Mashinaning marka nomi (data/car_brands.json — jadvaldagi "Brend" ustunidan). Ro'yxatda
    bo'lmasa (yangi qo'shilgan mashina) — nomining birinchi so'zi."""
    global _car_brand_map
    if _car_brand_map is None:
        try:
            _car_brand_map = json.loads(_BRANDS_JSON.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _car_brand_map = {}
    label = _car_brand_map.get(model)
    if label:
        return label
    first = model.strip().split()[0] if model.strip() else "Boshqa"
    return first[:1].upper() + first[1:]


def sub_slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") or "other"


def get_brand_slug(model: str) -> str:
    first_word = model.strip().split()[0].lower()
    for prefix, label in BRAND_PREFIXES:
        if first_word == prefix:
            return slugify_brand(label)
    if first_word in CHEVROLET_MODELS or car_brand_label(model) == "Chevrolet":
        return "chevrolet"
    return "other"


def brand_label(slug: str) -> str:
    """Asosiy guruh yoki "Boshqalar" ichidagi marka slug'idan ko'rinadigan nom."""
    if slug in BRAND_LABELS:
        return BRAND_LABELS[slug]
    for c in db.list_cars():
        if get_brand_slug(c["model"]) == "other":
            lbl = car_brand_label(c["model"])
            if sub_slug(lbl) == slug:
                return lbl
    return slug


def other_brands_with_counts():
    """"Boshqalar" ichidagi markalar: [(slug, label, count)], mashinasi ko'p markadan boshlab."""
    counts: dict = {}
    for c in db.list_cars():
        if get_brand_slug(c["model"]) == "other":
            lbl = car_brand_label(c["model"])
            counts[lbl] = counts.get(lbl, 0) + 1
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower()))
    return [(sub_slug(lbl), lbl, n) for lbl, n in items]


def brands_with_counts():
    """[(slug, label, count), ...] — faqat kamida 1 ta mashinasi bor brendlar, BRAND_ORDER tartibida."""
    cars = db.list_cars()
    counts = {}
    for c in cars:
        slug = get_brand_slug(c["model"])
        counts[slug] = counts.get(slug, 0) + 1
    return [(slug, BRAND_LABELS[slug], counts[slug]) for slug in BRAND_ORDER if counts.get(slug)]


def cars_for_brand(slug: str):
    cars = db.list_cars()
    if slug in BRAND_LABELS:
        return [c for c in cars if get_brand_slug(c["model"]) == slug]
    return [c for c in cars
            if get_brand_slug(c["model"]) == "other" and sub_slug(car_brand_label(c["model"])) == slug]
