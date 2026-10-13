"""Yandex Maps qidiruv havolasini API kalitsiz tuzish."""
from urllib.parse import quote


def yandex_search_url(query: str) -> str:
    return f"https://yandex.uz/maps/?text={quote(query)}"


def branch_maps_url(branch: dict) -> str:
    # Koordinata bo'lsa — aniq nuqta (marshrut bilan ochiladi); bo'lmasa — qidiruv
    if branch.get("latitude") and branch.get("longitude"):
        return f"https://yandex.uz/maps/?pt={branch['longitude']},{branch['latitude']}&z=17&l=map"
    query = f"Carland {branch['name']} {branch['address']}"
    return yandex_search_url(query)
