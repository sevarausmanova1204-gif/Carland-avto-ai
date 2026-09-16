"""Mashina rusumini avtomobil markasiga (brendiga) ajratish.

Baza jadvalida marka nomi har doim ham model nomida yozilmagan — masalan
GM/Chevrolet oilaviy modellar (Cobalt, Nexia, Captiva, Malibu...) faqat
o'zining nomi bilan saqlangan, marka ko'rsatilmagan. Shu sababli bunday
modellar uchun qo'lda tuzilgan ro'yxat orqali "Chevrolet" markasi biriktiriladi.
"""
from . import db

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


def get_brand_slug(model: str) -> str:
    first_word = model.strip().split()[0].lower()
    for prefix, label in BRAND_PREFIXES:
        if first_word == prefix:
            return slugify_brand(label)
    if first_word in CHEVROLET_MODELS:
        return "chevrolet"
    return "other"


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
    return [c for c in cars if get_brand_slug(c["model"]) == slug]
