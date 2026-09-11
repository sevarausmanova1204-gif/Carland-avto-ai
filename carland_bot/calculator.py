"""
Carland Moy Kalkulyatori
Avtomobil ma'lumotlari bo'yicha moy hajmi, turi va narxini hisoblab beruvchi modul.
"""

from typing import Dict, Any, Optional
from car_data import CARS_DATABASE, find_car_by_query
from carland_knowledge import POPULAR_OILS


def format_car_oil_report(car_info: Dict[str, Any], selected_oil_name: Optional[str] = None, lang: str = "uz") -> str:
    """
    Avtomobil uchun moy hisoboti matnini tayyorlaydi (O'zbek, Rus va Ingliz tillarida).
    """
    name = car_info["name"]
    brand = car_info["brand"]
    engine_oil = car_info.get("engine_oil", "-")
    engine_oil_type = car_info.get("engine_oil_type", "-")
    gearbox_oil = car_info.get("gearbox_oil", "-")
    gearbox_oil_type = car_info.get("gearbox_oil_type", "-")
    reductor_oil = car_info.get("reductor_oil", "-")
    filter_interval = car_info.get("filter_interval", "-")
    service_fee = car_info.get("service_fee", "")
    oil_filter = car_info.get("oil_filter", "")
    notes = car_info.get("notes", "")

    oil_filter_ru = f"   • Масляный фильтр: <b>{oil_filter}</b>\n" if oil_filter else ""
    oil_filter_en = f"   • Oil filter: <b>{oil_filter}</b>\n" if oil_filter else ""
    oil_filter_uz = f"   • Moy filtri: <b>{oil_filter}</b>\n" if oil_filter else ""

    if lang == "ru":
        text = (
            f"🚗 <b>Автомобиль:</b> {name} ({brand})\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛢 <b>Моторное масло:</b>\n"
            f"   • Объем: <b>{engine_oil}</b>\n"
            f"   • Рекомендуемый тип масла: <code>{engine_oil_type}</code>\n"
            f"{oil_filter_ru}\n"
            f"⚙️ <b>Масло в коробку передач:</b>\n"
            f"   • Объем: <b>{gearbox_oil}</b>\n"
            f"   • Тип масла: <code>{gearbox_oil_type}</code>\n\n"
        )
        if reductor_oil and reductor_oil != "-":
            text += (
                f"🔄 <b>Масло в редуктор:</b>\n"
                f"   • Объем и тип: <b>{reductor_oil}</b>\n\n"
            )
        if service_fee:
            text += f"💰 <b>Стоимость услуги:</b> <b>{service_fee}</b>\n\n"
        text += f"⏱ <b>Интервал замены фильтра:</b> {filter_interval}\n"
        if notes:
            text += f"💡 <b>Дополнительно:</b> <i>{notes}</i>\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        text += "🏷 <b>Популярные масла в наличии Carland:</b>\n"
        for oil_name, details in list(POPULAR_OILS.items())[:4]:
            price = details["price_per_liter"]
            formatted_price = f"{price:,}".replace(",", " ")
            text += f"• <b>{oil_name}</b> — {formatted_price} сум / 1Л\n"
        text += (
            "\n🛠 <i>При покупке моторного масла в сервисах Carland замена производится БЕСПЛАТНО!</i>\n"
            "⚠️ <b>Примечание:</b> <i>Бесплатная замена действует только на моторное масло. При замене масла в коробке передач и редукторе взимается оплата за услугу в зависимости от модели автомобиля.</i>\n"
            "📍 <i>Чтобы узнать ближайший филиал, нажмите /filiallar.</i>"
        )
    elif lang == "en":
        text = (
            f"🚗 <b>Vehicle:</b> {name} ({brand})\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛢 <b>Engine Oil:</b>\n"
            f"   • Capacity: <b>{engine_oil}</b>\n"
            f"   • Recommended viscosity: <code>{engine_oil_type}</code>\n"
            f"{oil_filter_en}\n"
            f"⚙️ <b>Transmission (Gearbox) Oil:</b>\n"
            f"   • Capacity: <b>{gearbox_oil}</b>\n"
            f"   • Oil specification: <code>{gearbox_oil_type}</code>\n\n"
        )
        if reductor_oil and reductor_oil != "-":
            text += (
                f"🔄 <b>Differential Oil:</b>\n"
                f"   • Capacity and type: <b>{reductor_oil}</b>\n\n"
            )
        if service_fee:
            text += f"💰 <b>Service fee:</b> <b>{service_fee}</b>\n\n"
        text += f"⏱ <b>Filter replacement interval:</b> {filter_interval}\n"
        if notes:
            text += f"💡 <b>Note:</b> <i>{notes}</i>\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        text += "🏷 <b>Available quality oils at Carland:</b>\n"
        for oil_name, details in list(POPULAR_OILS.items())[:4]:
            price = details["price_per_liter"]
            formatted_price = f"{price:,}".replace(",", " ")
            text += f"• <b>{oil_name}</b> — {formatted_price} UZS / 1L\n"
        text += (
            "\n🛠 <i>Free oil replacement service when purchasing engine oil at Carland!</i>\n"
            "⚠️ <b>Note:</b> <i>Free replacement applies strictly to engine oil only. Service fee for transmission and differential oil replacement depends on the vehicle model.</i>\n"
            "📍 <i>Find your nearest branch using /filiallar.</i>"
        )
    else:
        text = (
            f"🚗 <b>Avtomobil:</b> {name} ({brand})\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛢 <b>Dvigatel (Mator) moyi:</b>\n"
            f"   • Hajmi: <b>{engine_oil}</b>\n"
            f"   • Tavsiya qilinadigan moy turi: <code>{engine_oil_type}</code>\n"
            f"{oil_filter_uz}\n"
            f"⚙️ <b>Uzatmalar qutisi (Karobka) moyi:</b>\n"
            f"   • Hajmi: <b>{gearbox_oil}</b>\n"
            f"   • Moy turi: <code>{gearbox_oil_type}</code>\n\n"
        )
        if reductor_oil and reductor_oil != "-":
            text += (
                f"🔄 <b>Reduktor moyi:</b>\n"
                f"   • Hajmi va turi: <b>{reductor_oil}</b>\n\n"
            )
        if service_fee:
            text += f"💰 <b>Xizmat haqi (Usluga):</b> <b>{service_fee}</b>\n\n"
        text += f"⏱ <b>Filtr almashtirish oralig'i:</b> {filter_interval}\n"
        if notes:
            text += f"💡 <b>Qo'shimcha ma'lumot:</b> <i>{notes}</i>\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        text += "🏷 <b>Carland do'konida mavjud sifatli moylar:</b>\n"
        for oil_name, details in list(POPULAR_OILS.items())[:4]:
            price = details["price_per_liter"]
            formatted_price = f"{price:,}".replace(",", " ")
            text += f"• <b>{oil_name}</b> — {formatted_price} so'm / 1L\n"
        text += (
            "\n🛠 <i>Carland servislarida mator moyi xarid qilinganda, almashtirish xizmati bepul amalga oshiriladi!</i>\n"
            "⚠️ <b>Eslatma:</b> <i>Bepul almashtirish faqatgina mator moyi uchun amal qiladi. Karobka va reduktor moyini alishtirganda mashina rusumiga qarab xizmat haqi olinadi.</i>\n"
            "📍 <i>O'zingizga yaqin filialni bilish uchun /filiallar buyrug'ini bosing.</i>"
        )

    return text


def calculate_oil_cost(liters: float, price_per_liter: int) -> Dict[str, Any]:
    """Moy narxini litr bo'yicha hisoblash"""
    total = int(liters * price_per_liter)
    return {
        "liters": liters,
        "price_per_liter": price_per_liter,
        "total_cost": total,
        "formatted_total": f"{total:,}".replace(",", " ")
    }
