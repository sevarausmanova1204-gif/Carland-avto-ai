"""
Carland Avtoservis - Avtomobillar uchun moy va texnik ma'lumotlar bazasi
PDF ma'lumotlari (2-4 betlar) asosida to'liq shakllantirilgan.
"""

from typing import Dict, Any, List, Optional
import re

CAR_BRANDS = [
    "Chevrolet",
    "Kia",
    "Hyundai",
    "BYD",
    "Chery",
    "Changan (Deepal)",
    "Haval",
    "Jetour",
    "Zeekr",
    "Leapmotor",
    "Dongfeng",
    "Voyah",
    "GAC",
    "Volkswagen",
    "Boshqalar"
]

CARS_DATABASE: Dict[str, Dict[str, Any]] = {
    # === CHEVROLET / DAEWOO ===
    "damas_eski": {
        "name": "Damas (eski)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "Mexanika 1.3 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "1.3 litr (75w90)",
        "filter_interval": "20 000 km",
        "notes": "Mexanika karobka va reduktorga 75w90 quyiladi"
    },
    "damas_yangi": {
        "name": "Damas (yangi)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "2.5 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "1.3 litr (75w90)",
        "filter_interval": "20 000 km",
        "notes": "Yangi model Damas"
    },
    "labo": {
        "name": "Labo",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "Mexanika 1.3 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "1.3 litr (75w90)",
        "filter_interval": "20 000 km",
        "notes": "Kichik yuk avtomobili"
    },
    "matiz_3_slindir": {
        "name": "Matiz (oddiy 3 silindr, 0.8L)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "2.7 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "2 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "-",
        "filter_interval": "20 000 km",
        "notes": "3 silindrli 0.8L mator"
    },
    "matiz_best": {
        "name": "Matiz Best (4 silindr, 1.0L)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "2.5 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "-",
        "filter_interval": "20 000 km",
        "notes": "4 silindrli 1.0L mator"
    },
    "spark_1_0": {
        "name": "Spark 1.0",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "4 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "Mexanika 2.5 litr (75w90) / Avtomat 5 litr (ATF6)",
        "gearbox_oil_type": "75w90 / ATF6",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "1.0L dvigatel"
    },
    "spark_1_25": {
        "name": "Spark 1.25",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "Mexanika 2.5 litr (75w90) / Avtomat 5.5 litr (ATF6)",
        "gearbox_oil_type": "75w90 / ATF6",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "1.25L dvigatel"
    },
    "cobalt": {
        "name": "Cobalt",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "0w20, 5w30, 5w40",
        "gearbox_oil": "⚡️ Avtomat (AKPP) — Asosiy: 7 litr ATF6\n     🕹 Mexanika (MKPP): 2.5 litr 75w90",
        "gearbox_oil_type": "ATF6 (Avtomat) / 75w90 (Mexanika)",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Hozirda avtomobillar asosan Avtomat (7L ATF6). Matoriga 3.5 litr moy ketadi."
    },
    "cobalt_mexanika": {
        "name": "Cobalt (Mexanika)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Mexanika (MKPP)",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "Mexanika 2.5 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Mexanika uzatmalar qutisi (MKPP)"
    },
    "cobalt_avtomat": {
        "name": "Cobalt (Avtomat)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Avtomat (AKPP)",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "0w20, 5w30, 5w40",
        "gearbox_oil": "Avtomat 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Avtomat uzatmalar qutisi (AKPP) — Asosiy variant"
    },
    "gentra": {
        "name": "Gentra (Lacetti 1.5)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3.5 litr (yangi Gentra)",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "⚡️ Avtomat (AKPP) — Asosiy: 7 litr ATF6\n     🕹 Mexanika (MKPP): 2 litr 75w-90",
        "gearbox_oil_type": "ATF6 (Avtomat) / 75w-90 (Mexanika)",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Hozirda mexanika kamayganligi sababli asosan Avtomat (7L ATF6). Yangi Gentra matoriga 3.5 litr moy ketadi."
    },
    "gentra_mexanika": {
        "name": "Gentra (Mexanika)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Mexanika (MKPP)",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "Mexanika 2 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Mexanika uzatmalar qutisi (MKPP)"
    },
    "gentra_avtomat": {
        "name": "Gentra (Avtomat)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Avtomat (AKPP)",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "Avtomat 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Avtomat uzatmalar qutisi (AKPP)"
    },
    "nexia_1": {
        "name": "Nexia 1",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "SOHC: 3 litr | SOHC gibrid: 3.5 litr | DOHC: 3.8 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "Mexanika 2 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Mator turiga qarab: SOHC 3L, SOHC gibrid 3.5L, DOHC 3.8L"
    },
    "nexia_2": {
        "name": "Nexia 2",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "SOHC: 3 litr | SOHC gibrid: 3.5 litr | DOHC: 3.8 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "Mexanika 2 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "SOHC (1.5) yoki DOHC (1.6)"
    },
    "nexia_3": {
        "name": "Nexia 3 (Ravon R3)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "⚡️ Avtomat (AKPP) — Asosiy: 7 litr ATF6\n     🕹 Mexanika (MKPP): 2 litr 75w-90",
        "gearbox_oil_type": "ATF6 (Avtomat) / 75w-90 (Mexanika)",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Hozirda asosan Avtomat (7L ATF6). Matoriga 3.5 litr moy ketadi."
    },
    "nexia_3_mexanika": {
        "name": "Nexia 3 (Mexanika)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Mexanika (MKPP)",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "Mexanika 2 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Mexanika uzatmalar qutisi (MKPP)"
    },
    "nexia_3_avtomat": {
        "name": "Nexia 3 (Avtomat)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Avtomat (AKPP)",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "Avtomat 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Avtomat uzatmalar qutisi (AKPP)"
    },
    "spark": {
        "name": "Spark (1.25 / 1.0)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "1.25L: 3.5 litr | 1.0L: 4 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "⚡️ Avtomat: 5.5 litr | 🕹 Mexanika: 2.5 litr",
        "gearbox_oil_type": "ATF6 (Avtomat) / 75w90 (Mexanika)",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Avtomatga 5.5L ATF6, mexanikaga 2.5L 75w90."
    },
    "lacetti": {
        "name": "Lacetti (1.6 / 1.8)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3.5 - 3.8 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "⚡️ Avtomat: 7 litr | 🕹 Mexanika: 2 litr",
        "gearbox_oil_type": "ATF6 (Avtomat) / 75w-90 (Mexanika)",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Prokladka va filtr almashadi."
    },
    "spark_mexanika": {
        "name": "Spark (Mexanika)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Mexanika (MKPP)",
        "engine_oil": "3.5 litr (1.25L) / 4 litr (1.0L)",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "Mexanika 2.5 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Mexanika uzatmalar qutisi (MKPP)"
    },
    "spark_avtomat": {
        "name": "Spark (Avtomat)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Avtomat (AKPP)",
        "engine_oil": "3.5 litr (1.25L) / 4 litr (1.0L)",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "Avtomat 5.5 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Avtomat uzatmalar qutisi (AKPP)"
    },
    "lacetti_mexanika": {
        "name": "Lacetti (Mexanika)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Mexanika (MKPP)",
        "engine_oil": "3.5 - 3.8 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "Mexanika 2 litr",
        "gearbox_oil_type": "75w90",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Praklatka va filtr almashadi"
    },
    "lacetti_avtomat": {
        "name": "Lacetti (Avtomat)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "transmission": "Avtomat (AKPP)",
        "engine_oil": "3.5 - 3.8 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "Avtomat 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Avtomat karobka (AKPP)"
    },
    "onix": {
        "name": "Chevrolet Onix (1.2 / 1.2 Turbo)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "4 litr",
        "engine_oil_type": "0w20, 5w30 Dexos1",
        "gearbox_oil": "Avtomat: 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "25 000 km",
        "notes": "Dexos1 Gen2/Gen3 sertifikatli 0w20 / 5w30 tavsiya etiladi"
    },
    "malibu_1": {
        "name": "Malibu 1",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "4.5 litr yoki 5 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "50 000 km",
        "notes": "2.4L dvigatel"
    },
    "malibu_2": {
        "name": "Malibu 2 (1.5T / 2.0T)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "5 litr",
        "engine_oil_type": "0w20",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "110 000 km",
        "notes": "Matorga 0w20 sintetik moy tavsiya etiladi"
    },
    "tracker_1": {
        "name": "Tracker 1 (1.8L)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "4 - 4.5 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "50 000 km",
        "notes": "ATF6 avtomat karobka moyi"
    },
    "tracker_2": {
        "name": "Tracker 2 (1.0T / 1.2T)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "4 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "0w20 yoki 5w30 Dexos1 moyi"
    },
    "captiva_1": {
        "name": "Captiva 1 (3.2L)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "7 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "6 litr",
        "gearbox_oil_type": "ATF 3",
        "reductor_oil": "1 litr (75w90)",
        "filter_interval": "55 000 km",
        "notes": "3.2L 6 silindrli mator"
    },
    "captiva_2_3": {
        "name": "Captiva 2 va 3 (2.4L / 3.0L)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "2.4 = 4.5 litr | 3.0 = 6 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "ATF 6",
        "reductor_oil": "1 litr (75w90)",
        "filter_interval": "45 000 km",
        "notes": "2.4L uchun 4.5L, 3.0L uchun 6L"
    },
    "captiva_4": {
        "name": "Captiva 4 (2.4L)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "4.5 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "ATF 6",
        "reductor_oil": "1 litr (75w90)",
        "filter_interval": "50 000 km",
        "notes": "2.4L dvigatel"
    },
    "captiva_5": {
        "name": "Captiva 5 (1.5L Turbo)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "4.5 litr",
        "engine_oil_type": "5w30, 5w40, 10w40",
        "gearbox_oil": "6 - 6.5 litr",
        "gearbox_oil_type": "CVT / ATF 6",
        "reductor_oil": "-",
        "filter_interval": "95 000 km",
        "notes": "1.5 Turbina mator, CVT variator karobka"
    },
    "tahoe": {
        "name": "Tahoe (5.2L / 5.3L / 6.2L)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "7.5 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "9 litr",
        "gearbox_oil_type": "ATF-8",
        "reductor_oil": "2 litr (75w90)",
        "filter_interval": "60 000 km",
        "notes": "ATF-8 uzatmalar qutisi moyi"
    },
    "equinox": {
        "name": "Equinox (2.0 Turbo)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "5.5 litr",
        "engine_oil_type": "0w20, 5w30 Dexos1",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "1 litr (75w90)",
        "filter_interval": "50 000 km",
        "notes": "2.0 Turbo mator"
    },
    "traverse": {
        "name": "Traverse (3.6L V6)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "6 litr",
        "engine_oil_type": "5w30 Dexos1",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "1 litr (75w90)",
        "filter_interval": "50 000 km",
        "notes": "3.6L V6 mator"
    },
    "monza_320t": {
        "name": "Monza 320T (1.5L Atmosfera)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "4 litr",
        "gearbox_oil_type": "DCT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "1.5 ATMO, 4L DCT karobka moyi"
    },
    "monza_330t": {
        "name": "Monza 330T (1.3L Turbo)",
        "brand": "Chevrolet",
        "category": "Chevrolet",
        "engine_oil": "5 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "1.3 Turbo, 7L ATF6 karobka moyi"
    },

    # === KIA ===
    "kia_k5": {
        "name": "Kia K5",
        "brand": "Kia",
        "category": "Kia",
        "engine_oil": "2.0L: 4 litr | 2.5L: 6 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "6 - 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "2.0 matorga 4L, 2.5 matorga 6L"
    },
    "kia_sorento": {
        "name": "Kia Sorento",
        "brand": "Kia",
        "category": "Kia",
        "engine_oil": "6 litr (2.5L - 3.5L)",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "6 - 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "1 litr (75w90)",
        "filter_interval": "50 000 km",
        "notes": "2.5-3.5 matorligi uchun 6 litr"
    },
    "kia_k8": {
        "name": "Kia K8",
        "brand": "Kia",
        "category": "Kia",
        "engine_oil": "6 litr (3.5L)",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "6 - 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "50 000 km",
        "notes": "3.5 mator 6 litr"
    },
    "kia_sonet": {
        "name": "Kia Sonet",
        "brand": "Kia",
        "category": "Kia",
        "engine_oil": "3.5 - 3.8 litr (1.5L)",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "6 litr",
        "gearbox_oil_type": "CVT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "1.5 mator, CVT variator"
    },
    "kia_sportage": {
        "name": "Kia Sportage",
        "brand": "Kia",
        "category": "Kia",
        "engine_oil": "2.0L: 4.5 litr | 2.5L: 6 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "6 - 7 litr",
        "gearbox_oil_type": "ATF esp4",
        "reductor_oil": "1 litr (75w90)",
        "filter_interval": "45 000 km",
        "notes": "2.0 mator 4.5L, 2.5 mator 6L"
    },
    "kia_seltos": {
        "name": "Kia Seltos",
        "brand": "Kia",
        "category": "Kia",
        "engine_oil": "4 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "6 litr",
        "gearbox_oil_type": "CVT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "4L mator moyi, CVT karobka"
    },

    # === HYUNDAI ===
    "hyundai_santa_fe": {
        "name": "Hyundai Santa Fe",
        "brand": "Hyundai",
        "category": "Hyundai",
        "engine_oil": "2.4L: 4.5 litr | 2.5L: 6 litr | 3.5L: 6 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "6 - 7 litr",
        "gearbox_oil_type": "ATF6 / CVT",
        "reductor_oil": "1 litr (75w90)",
        "filter_interval": "50 000 km",
        "notes": "Mator hajmiga qarab 4.5L dan 6L gacha"
    },
    "hyundai_i30": {
        "name": "Hyundai i30",
        "brand": "Hyundai",
        "category": "Hyundai",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "6 - 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "3.5 litr matorga"
    },
    "hyundai_tucson": {
        "name": "Hyundai Tucson",
        "brand": "Hyundai",
        "category": "Hyundai",
        "engine_oil": "2.0L: 4.5 litr | 2.5L: 6 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "6 - 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "1 litr (75w90)",
        "filter_interval": "45 000 km",
        "notes": "2.0L uchun 4.5L, 2.5L uchun 6L"
    },
    "hyundai_elantra": {
        "name": "Hyundai Elantra",
        "brand": "Hyundai",
        "category": "Hyundai",
        "engine_oil": "1.5L: 3.5L | 1.6L: 3.5L | 2.0L: 4.5L",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "6 - 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "1.5/1.6L ga 3.5 litr, 2.0L ga 4.5 litr"
    },
    "hyundai_creta": {
        "name": "Hyundai Creta",
        "brand": "Hyundai",
        "category": "Hyundai",
        "engine_oil": "1.6L: 3.5 litr | 2.0L: 4.5 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "6 - 7 litr",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "1.6L ga 3.5L, 2.0L ga 4.5L"
    },

    # === CHERY ===
    "chery_tiggo_2_pro": {
        "name": "Chery Tiggo 2 Pro",
        "brand": "Chery",
        "category": "Chery",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "6 litr",
        "gearbox_oil_type": "CVT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "CVT variator karobka"
    },
    "chery_tiggo_4_pro": {
        "name": "Chery Tiggo 4 Pro",
        "brand": "Chery",
        "category": "Chery",
        "engine_oil": "4.5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "6 litr",
        "gearbox_oil_type": "CVT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "CVT variator karobka"
    },
    "chery_tiggo_7_pro": {
        "name": "Chery Tiggo 7 Pro",
        "brand": "Chery",
        "category": "Chery",
        "engine_oil": "5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "6 litr",
        "gearbox_oil_type": "CVT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "Matorga 5L, CVT karobkaga 6L"
    },
    "chery_tiggo_8_pro": {
        "name": "Chery Tiggo 8 Pro",
        "brand": "Chery",
        "category": "Chery",
        "engine_oil": "4.5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "6 litr",
        "gearbox_oil_type": "CVT / DCT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "Matorga 4.5L, karobkaga 6L"
    },
    "chery_tiggo_9": {
        "name": "Chery Tiggo 9",
        "brand": "Chery",
        "category": "Chery",
        "engine_oil": "5 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "7 litr",
        "gearbox_oil_type": "DCT / AT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "2.0 Turbo mator"
    },
    "chery_arrizo_6_pro": {
        "name": "Chery Arrizo 6 Pro",
        "brand": "Chery",
        "category": "Chery",
        "engine_oil": "5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "6 litr",
        "gearbox_oil_type": "CVT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "Matorga 5 litr, karobkaga 6L CVT"
    },
    "chery_aicar_eq7": {
        "name": "Chery Aiqar EQ7 (eQ7)",
        "brand": "Chery",
        "category": "Chery",
        "engine_oil": "-",
        "engine_oil_type": "To'liq elektr (Dvigatel moyi yo'q)",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2 litr (EV moy)",
        "filter_interval": "30 000 km",
        "notes": "To'liq elektr (full electric): Reduktorga 2 litr EV moy quyiladi"
    },

    # === BYD (Elektromobillar va Gibridlar) ===
    "byd_song_plus": {
        "name": "BYD Song Plus (DM-i / EV)",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "3.5 litr (DM-i gibrid)",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.2 - 3 litr (EV reduktor moyi)",
        "filter_interval": "20 000 km (reduktor)",
        "notes": "Gibrid dvigateliga 3.5L, reduktorga 2.2-3L maxsus EV moy"
    },
    "byd_song_pro": {
        "name": "BYD Song Pro (DM-i / ICE)",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "3.5 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "3 litr (EV)",
        "filter_interval": "20 000 km",
        "notes": "DM-i matoriga 3.5L, reduktorga 3L EV"
    },
    "byd_song_l": {
        "name": "BYD Song L (EV / DM-i)",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "3.5 litr (DM-i bo'lsa)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "3 litr (EV)",
        "filter_interval": "20 000 km",
        "notes": "Reduktorga 3L EV moy"
    },
    "byd_yuan_plus": {
        "name": "BYD Yuan Plus (Atto 3)",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "To'liq elektr, reduktorga 1 litr EV moy"
    },
    "byd_yuan_up": {
        "name": "BYD Yuan Up (Gibrid)",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "4 litr",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.2 litr (EV moy)",
        "filter_interval": "25 000 km",
        "notes": "Gibrid: Mator moyi 4L (0w20), Reduktor moyi 2.2L (EV moy)"
    },
    "byd_full_electric": {
        "name": "BYD To'liq Elektr (EV)",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "-",
        "engine_oil_type": "To'liq elektr (Mator moyi mavjud emas)",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1 litr (EV moy)",
        "filter_interval": "30 000 km",
        "notes": "BYD to'liq elektr modellar: Reduktorga 1 litr EV moy"
    },
    "byd_qin_plus": {
        "name": "BYD Qin Plus (DM-i / EV)",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "3.5 litr (DM-i)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "Oldi: 1 litr, Orqa: 1 litr (EV)",
        "filter_interval": "20 000 km",
        "notes": "Oldi 1L, orqa 1L EV reduktor moyi"
    },
    "byd_han": {
        "name": "BYD Han (EV / DM-p)",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "3.5 litr (DM-p gibrid)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "Oldi: 1 litr, Orqa: 2 litr (EV)",
        "filter_interval": "20 000 km",
        "notes": "AWD modelda oldi 1L, orqa 2L EV moy"
    },
    "byd_dolphin": {
        "name": "BYD Dolphin",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "To'liq elektr, reduktorga 1 litr EV moy"
    },
    "byd_seal": {
        "name": "BYD Seal",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 1 litr EV moy"
    },
    "byd_seal_u": {
        "name": "BYD Seal U",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "3.5 litr (DM-i)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 1 litr EV moy"
    },
    "byd_e2": {
        "name": "BYD E2",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 1 litr EV moy"
    },
    "byd_destroyer_05": {
        "name": "BYD Destroyer 05 (Champion)",
        "brand": "BYD",
        "category": "BYD",
        "engine_oil": "3.5 litr (gibrid)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.5 litr (EV)",
        "filter_interval": "25 000 km",
        "notes": "Reduktorga 2.5L EV moy"
    },

    # === CHANGAN / DEEPAL ===
    "deepal_sl03_hybrid": {
        "name": "Deepal SL03 (Gibrid)",
        "brand": "Changan",
        "category": "Changan",
        "engine_oil": "4 litr",
        "engine_oil_type": "0w20",
        "oil_filter": "OP 621",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV / D2",
        "reductor_oil": "1.5 litr (EV/D2 moy)",
        "filter_interval": "20 000 km",
        "notes": "Gibrid: Mator moyi 4L 0w20, Moy filtri: OP 621, Reduktorga 1.5L EV/D2 moy quyiladi"
    },

    # === VOYAH ===
    "voyah_free": {
        "name": "Voyah Free (Hybrid / Full EV)",
        "brand": "Voyah",
        "category": "Voyah",
        "engine_oil": "4 litr (Hybrid generator matori)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.5 - 3.5 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Gibrid generatoriga 4L, reduktorga 2.5-3.5L EV"
    },
    "voyah_passion": {
        "name": "Voyah Passion",
        "brand": "Voyah",
        "category": "Voyah",
        "engine_oil": "4 litr (gibrid bo'lsa)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "3 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Premium elektr/gibrid sedan"
    },
    "voyah_dream": {
        "name": "Voyah Dream",
        "brand": "Voyah",
        "category": "Voyah",
        "engine_oil": "4 litr (gibrid)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "3.5 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Premium miniven"
    },

    # === LEAPMOTOR ===
    "leapmotor_t03": {
        "name": "Leapmotor T03",
        "brand": "Leapmotor",
        "category": "Leapmotor",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.3 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 2.3L EV moy"
    },
    "leapmotor_c01": {
        "name": "Leapmotor C01",
        "brand": "Leapmotor",
        "category": "Leapmotor",
        "engine_oil": "3.5L (EREV gibrid bo'lsa)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.3 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 2.3L EV moy"
    },
    "leapmotor_c11": {
        "name": "Leapmotor C11",
        "brand": "Leapmotor",
        "category": "Leapmotor",
        "engine_oil": "3.5L (EREV gibrid bo'lsa)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.3 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 2.3L EV moy"
    },
    "leapmotor_c10": {
        "name": "Leapmotor C10",
        "brand": "Leapmotor",
        "category": "Leapmotor",
        "engine_oil": "3.5L (EREV gibrid)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.3 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 2.3L EV moy"
    },
    "leapmotor_b10": {
        "name": "Leapmotor B10",
        "brand": "Leapmotor",
        "category": "Leapmotor",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.3 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 2.3L EV moy"
    },
    "leapmotor_d19": {
        "name": "Leapmotor D19",
        "brand": "Leapmotor",
        "category": "Leapmotor",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "2.3 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 2.3L EV moy"
    },

    # === DONGFENG ===
    "dongfeng_ep_007": {
        "name": "Dongfeng Eπ 007",
        "brand": "Dongfeng",
        "category": "Dongfeng",
        "engine_oil": "3.5L (gibrid)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1.5 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 1.5L EV moy"
    },
    "dongfeng_e5": {
        "name": "Dongfeng E5",
        "brand": "Dongfeng",
        "category": "Dongfeng",
        "engine_oil": "3.5L (gibrid)",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1.5 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 1.5L EV moy"
    },
    "dongfeng_008": {
        "name": "Dongfeng 008",
        "brand": "Dongfeng",
        "category": "Dongfeng",
        "engine_oil": "4L (gibrid)",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1.5 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 1.5L EV moy"
    },
    "dongfeng_aeolus_shine": {
        "name": "Dongfeng Aeolus Shine",
        "brand": "Dongfeng",
        "category": "Dongfeng",
        "engine_oil": "4 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "4 litr",
        "gearbox_oil_type": "DCT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "4L mator, 4L DCT karobka moyi"
    },

    # === ZEEKR ===
    "zeekr_001": {
        "name": "Zeekr 001",
        "brand": "Zeekr",
        "category": "Zeekr",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "ATF6 / EV",
        "reductor_oil": "Oldi: ATF6 | Orqa: 2 litr | Reduktor: 1.2 litr",
        "filter_interval": "30 000 km",
        "notes": "Old reduktorga ATF6, orqa reduktorga 2 litr"
    },
    "zeekr_x": {
        "name": "Zeekr X",
        "brand": "Zeekr",
        "category": "Zeekr",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "ATF6 / EV",
        "reductor_oil": "Oldi: ATF6 | Orqa: 2 litr | Reduktor: 1.2 litr",
        "filter_interval": "30 000 km",
        "notes": "Old reduktorga ATF6, orqa reduktorga 2 litr"
    },

    # === AITO ===
    "aito_m9": {
        "name": "Aito M9 (Range Extender)",
        "brand": "Aito",
        "category": "Boshqalar",
        "engine_oil": "4 litr",
        "engine_oil_type": "0w20",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1.5 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Range extender generator matori 4L, reduktor 1.5L EV"
    },

    # === JETOUR ===
    "jetour_dashing": {
        "name": "Jetour Dashing",
        "brand": "Jetour",
        "category": "Jetour",
        "engine_oil": "4.5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "5.5 litr",
        "gearbox_oil_type": "DCT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "Matorga 4.5L, DCT karobkaga 5.5L"
    },
    "jetour_x90": {
        "name": "Jetour X90",
        "brand": "Jetour",
        "category": "Jetour",
        "engine_oil": "5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "6 litr",
        "gearbox_oil_type": "CVT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "Matorga 5L, CVT karobkaga 6L"
    },

    # === HAVAL ===
    "haval_h6": {
        "name": "Haval H6",
        "brand": "Haval",
        "category": "Haval",
        "engine_oil": "4.5 - 6 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "5 litr",
        "gearbox_oil_type": "DCT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "Matorga 4.5L-6L, 5L DCT karobka moyi"
    },
    "haval_jolion": {
        "name": "Haval Jolion",
        "brand": "Haval",
        "category": "Haval",
        "engine_oil": "4.5 litr",
        "engine_oil_type": "0w20, 5w30",
        "gearbox_oil": "5 litr",
        "gearbox_oil_type": "DCT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "Matorga 4.5L, 5L DCT karobka moyi"
    },
    "haval_m6": {
        "name": "Haval M6",
        "brand": "Haval",
        "category": "Haval",
        "engine_oil": "4.5 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "5 litr",
        "gearbox_oil_type": "DCT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "Matorga 4.5L, 5L DCT karobka moyi"
    },

    # === BESTUNE ===
    "bestune_t55": {
        "name": "Bestune T55",
        "brand": "Bestune",
        "category": "Boshqalar",
        "engine_oil": "4 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "4 litr",
        "gearbox_oil_type": "DCT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "Matorga 4L, DCT karobkaga 4L"
    },

    # === LADA ===
    "lada_vesta_cross": {
        "name": "Lada Vesta Cross",
        "brand": "Lada",
        "category": "Boshqalar",
        "engine_oil": "4 - 4.5 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "5.5 litr",
        "gearbox_oil_type": "CVT",
        "reductor_oil": "-",
        "filter_interval": "40 000 km",
        "notes": "CVT variator karobkaga 5.5L"
    },

    # === HONGQI ===
    "hongqi_eqm5": {
        "name": "Hongqi EQM5",
        "brand": "Hongqi",
        "category": "Boshqalar",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "ATF6",
        "reductor_oil": "1.5 litr (ATF6)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 1.5L ATF6"
    },

    # === GAC ===
    "gac_aion_v": {
        "name": "GAC Aion V",
        "brand": "GAC",
        "category": "Boshqalar",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "0.7 litr (EV)",
        "filter_interval": "30 000 km",
        "notes": "Reduktorga 0.7 litr EV moy"
    },

    # === BMW ===
    "bmw_i3_i4_i5": {
        "name": "BMW (i3, i4, i5)",
        "brand": "BMW",
        "category": "Boshqalar",
        "engine_oil": "-",
        "engine_oil_type": "Elektromobil",
        "gearbox_oil": "-",
        "gearbox_oil_type": "75W-90",
        "reductor_oil": "2.5 litr (75W-90)",
        "filter_interval": "40 000 km",
        "notes": "Elektr modellar reduktoriga 2.5L 75W-90"
    },

    # === VOLKSWAGEN ===
    "volkswagen_id4": {
        "name": "Volkswagen ID.4",
        "brand": "Volkswagen",
        "category": "Volkswagen",
        "engine_oil": "-",
        "engine_oil_type": "To'liq elektr (Dvigatel moyi yo'q)",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV / D1",
        "reductor_oil": "1 litr (D1 / EV moylar)",
        "filter_interval": "30 000 km",
        "notes": "To'liq elektr: Reduktorga 1 litr D1 / EV maxsus moyi quyiladi"
    },
    "volkswagen_id6": {
        "name": "Volkswagen ID.6",
        "brand": "Volkswagen",
        "category": "Volkswagen",
        "engine_oil": "-",
        "engine_oil_type": "To'liq elektr (Dvigatel moyi yo'q)",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV / D2",
        "reductor_oil": "Oldi: 600 gr (EV/D2), Orqa: 1 litr (EV/D2)",
        "filter_interval": "30 000 km",
        "notes": "To'liq elektr: Reduktorga oldiga 600 gr EV/D2, orqaga 1 litr EV/D2 moyi quyiladi"
    },
    "volkswagen_caddy": {
        "name": "Volkswagen Caddy",
        "brand": "Volkswagen",
        "category": "Volkswagen",
        "engine_oil": "4 litr",
        "engine_oil_type": "5w30, 5w40",
        "gearbox_oil": "2 litr",
        "gearbox_oil_type": "75W-85",
        "reductor_oil": "-",
        "filter_interval": "30 000 km",
        "notes": "Matorga 4L, karobkaga 2L 75W-85"
    },

    # === SKODA ===
    "skoda_kodiaq": {
        "name": "Skoda Kodiaq",
        "brand": "Skoda",
        "category": "Boshqalar",
        "engine_oil": "5.5 litr",
        "engine_oil_type": "5w30",
        "gearbox_oil": "5.5 litr (DSG)",
        "gearbox_oil_type": "DSG",
        "reductor_oil": "2.5 litr (Castrol-D2)",
        "filter_interval": "45 000 km",
        "notes": "DSG karobkaga 5.5L, reduktorga 2.5L Castrol-D2"
    },

    # === GAC ===
    "gac_aion_s_plus": {
        "name": "GAC Aion S+",
        "brand": "GAC",
        "category": "GAC",
        "engine_oil": "-",
        "engine_oil_type": "To'liq elektr (EV)",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1 litr (EV moy)",
        "service_fee": "200 000 so'm",
        "filter_interval": "30 000 km",
        "notes": "To'liq elektr (EV). Reduktor moyi: 1 litr EV moy + 200 000 so'm xizmat haqi (usluga)."
    },
    "gac_aion_s": {
        "name": "GAC Aion S",
        "brand": "GAC",
        "category": "GAC",
        "engine_oil": "-",
        "engine_oil_type": "To'liq elektr (EV)",
        "gearbox_oil": "-",
        "gearbox_oil_type": "EV",
        "reductor_oil": "1 litr (EV moy)",
        "service_fee": "200 000 so'm",
        "filter_interval": "30 000 km",
        "notes": "To'liq elektr (EV). Reduktor moyi: 1 litr EV moy + 200 000 so'm xizmat haqi (usluga)."
    }
}


# Ikkala uzatmalar qutisi (Mexanika va Avtomat) variantlari mavjud avtomobillar
DUAL_TRANSMISSION_CARS = {
    "cobalt": {
        "name": "Chevrolet Cobalt",
        "mexanika": "cobalt_mexanika",
        "avtomat": "cobalt_avtomat"
    },
    "gentra": {
        "name": "Chevrolet Gentra",
        "mexanika": "gentra_mexanika",
        "avtomat": "gentra_avtomat"
    },
    "nexia_3": {
        "name": "Chevrolet Nexia 3",
        "mexanika": "nexia_3_mexanika",
        "avtomat": "nexia_3_avtomat"
    },
    "spark": {
        "name": "Chevrolet Spark",
        "mexanika": "spark_mexanika",
        "avtomat": "spark_avtomat"
    },
    "lacetti": {
        "name": "Chevrolet Lacetti",
        "mexanika": "lacetti_mexanika",
        "avtomat": "lacetti_avtomat"
    }
}


def find_car_by_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Foydalanuvchi yozgan matn ichidan avtomobil modelini aniqlaydi.
    Agar avtomobilning ikkala (Mexanika va Avtomat) varianti bo'lsa va matnda
    aniqlashtirilmagan bo'lsa, 'needs_transmission': True qaytaradi.
    """
    try:
        from smart_intent import normalize_query_text
        cleaned = normalize_query_text(query)
    except Exception:
        cleaned = query.lower().strip()
        cleaned = re.sub(r'[\'\"`’]', '', cleaned)
    
    is_avtomat = any(w in cleaned for w in ["avtomat", "akpp", "avtomati", "avtomatiga"])
    is_mexanika = any(w in cleaned for w in ["mexanika", "mkpp", "mexanikasi", "mexanikasiga", "mexan"])

    # 0. Maxsus mashinalar uchun tezkor aniqlash
    if any(w in cleaned for w in ["sl03", "sl 03", "deepal", "depal", "дипал", "депал"]):
        return CARS_DATABASE["deepal_sl03_hybrid"]
    if any(w in cleaned for w in ["eq7", "eq 7", "aiqar", "aicar", "айкар", "эку7"]):
        return CARS_DATABASE["chery_aicar_eq7"]
    if any(w in cleaned for w in ["id 6", "id.6", "id6", "volkswagen id6", "volkswagen id 6", "volswagen id 6", "voltswagen id 6", "фольксваген ид 6", "фольксваген ид6", "vw id6", "vw id 6"]):
        return CARS_DATABASE["volkswagen_id6"]
    if any(w in cleaned for w in ["id 4", "id.4", "id4", "volkswagen id", "volkswagen id4", "volkswagen id 4", "volswagen id 4", "voltswagen id 4", "фольксваген ид 4", "фольксваген ид4", "vw id4", "vw id 4"]):
        return CARS_DATABASE["volkswagen_id4"]
    if any(w in cleaned for w in ["caddy", "кадди"]):
        return CARS_DATABASE["volkswagen_caddy"]
    if any(w in cleaned for w in ["byd_ev", "byd ev", "byd full electr", "byd full electric", "byd toliq elektr", "byd to'liq elektr", "full electr", "full electric"]):
        return CARS_DATABASE["byd_full_electric"]
    if any(w in cleaned for w in ["aion s+", "aion s", "aion", "gac"]):
        return CARS_DATABASE["gac_aion_s_plus"]
    if any(w in cleaned for w in ["yuan_up", "yuan up", "yuanup"]):
        return CARS_DATABASE["byd_yuan_up"]
    if any(w in cleaned for w in ["yuan_plus", "yuan plus"]):
        return CARS_DATABASE["byd_yuan_plus"]
    if "song" in cleaned:
        return CARS_DATABASE["byd_song_plus"]
    if any(w in cleaned for w in ["chazor", "destroyer"]):
        return CARS_DATABASE["byd_destroyer_05"]
    if "tracker" in cleaned:
        if any(w in cleaned for w in ["1", "eski", "1.8"]):
            return CARS_DATABASE["tracker_1"]
        return CARS_DATABASE["tracker_2"]
    if "malibu" in cleaned:
        if any(w in cleaned for w in ["1", "eski"]):
            return CARS_DATABASE["malibu_1"]
        return CARS_DATABASE["malibu_2"]
    if "damas" in cleaned:
        if "eski" in cleaned:
            return CARS_DATABASE["damas_eski"]
        return CARS_DATABASE["damas_yangi"]
    if "labo" in cleaned:
        return CARS_DATABASE["labo"]
    if "nexia 3" in cleaned or "nexia_3" in cleaned:
        if is_avtomat:
            return CARS_DATABASE["nexia_3_avtomat"]
        elif is_mexanika:
            return CARS_DATABASE["nexia_3_mexanika"]
        return CARS_DATABASE["nexia_3"]

    # 1. Ikkala varianti bor mashinalarni tekshirish (Cobalt, Gentra, Nexia 3, Spark, Lacetti)
    for code, info in DUAL_TRANSMISSION_CARS.items():
        search_terms = [code.replace("_", " "), code]
        if any(term in cleaned for term in search_terms):
            if is_avtomat:
                return CARS_DATABASE[info["avtomat"]]
            elif is_mexanika:
                return CARS_DATABASE[info["mexanika"]]
            else:
                # Avtomat birinchi o'rinda bo'lgan to'liq modelni qaytaramiz (Mator 3.5L, Avtomat 7L, Mexanika 2L)
                return CARS_DATABASE.get(code, CARS_DATABASE[info["avtomat"]])

    # 2. To'g'ridan-to'g'ri kalit yoki to'liq nom mosligi
    for key, data in CARS_DATABASE.items():
        if key == cleaned or data["name"].lower() == cleaned:
            return data

    # 3. Mashina nomidagi asosiy so'zlar bo'yicha
    for key, data in CARS_DATABASE.items():
        base_model = key.split("_")[0]
        if base_model in cleaned:
            digits = re.findall(r'\d+', cleaned)
            if digits:
                if any(d in key for d in digits):
                    return data
            else:
                return data

    # 4. Model nomining so'zlari bo'yicha qidiruv
    for key, data in CARS_DATABASE.items():
        name_clean = re.sub(r'[^a-zA-Z0-9\s]', '', data["name"].lower())
        words = [w for w in name_clean.split() if len(w) >= 2]
        query_words = set(cleaned.split())
        if any(w in query_words or (len(w) >= 3 and w in cleaned) for w in words):
            return data

    return None


def get_cars_by_category(category: str) -> List[Dict[str, Any]]:
    """Kategoriya yoki marka bo'yicha mashinalar ro'yxatini qaytaradi"""
    # Chevrolet uchun ikkilanuvchi modellarni bitta umumiy nom bilan ko'rsatamiz
    if category == "Chevrolet":
        unique_cars = []
        seen = set()
        for key, c in CARS_DATABASE.items():
            if c["category"] != "Chevrolet":
                continue
            base = key.split("_")[0]
            if base in ["cobalt", "gentra", "spark", "lacetti"]:
                if base not in seen:
                    seen.add(base)
                    info = DUAL_TRANSMISSION_CARS[base]
                    unique_cars.append({
                        "name": info["name"],
                        "dual_code": base
                    })
            elif "nexia_3" in key:
                if "nexia_3" not in seen:
                    seen.add("nexia_3")
                    unique_cars.append({
                        "name": "Chevrolet Nexia 3",
                        "dual_code": "nexia_3"
                    })
            else:
                unique_cars.append(c)
        return unique_cars

    if category in ["Changan", "Deepal", "Changan (Deepal)"]:
        return [c for c in CARS_DATABASE.values() if c.get("category") in ["Changan", "Deepal", "Changan (Deepal)"]]

    return [c for c in CARS_DATABASE.values() if c["category"] == category]

