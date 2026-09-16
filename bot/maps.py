"""Yandex Maps qidiruv havolasini API kalitsiz tuzish."""
from urllib.parse import quote


def yandex_search_url(query: str) -> str:
    return f"https://yandex.uz/maps/?text={quote(query)}"


def branch_maps_url(branch: dict) -> str:
    query = f"Carland {branch['name']} {branch['address']}"
    return yandex_search_url(query)
