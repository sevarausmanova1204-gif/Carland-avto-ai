"""
Carland umumiy ma'lumotlari, filiallar, maxsus atamalar va do'kon narxlar bazasi.
PDF ma'lumotlari asosida to'liq shakllantirilgan.
"""

# Carland 15 ta filiali manzillari, aniq ish vaqtlari va lokatsiya havolalari (Taplink)
CARLAND_BRANCHES = [
    {
        "name": "Chig'atoy filiali",
        "name_ru": "Филиал Чигатай",
        "name_en": "Chigatoy Branch",
        "city": "Toshkent",
        "city_ru": "Ташкент",
        "city_en": "Tashkent",
        "address": "Chig'atoy",
        "address_ru": "массив Чигатай",
        "address_en": "Chigatoy residential area",
        "orientr": "Chig'atoy masjiddan kelganda Tuning House'dan o'tib o'ng qo'lda; Uzgaradok chorrahasidan Chimboyga qarab kelishda Voyah servis yonida chap qo'lda.",
        "orientr_ru": "Со стороны мечети Чигатай проехать Tuning House — справа; со стороны перекрестка Узгарадок в сторону Чимбоя — возле сервиса Voyah слева.",
        "orientr_en": "Coming from Chigatoy Mosque past Tuning House on the right; coming from Uzgaradok intersection towards Chimboy next to Voyah service on the left.",
        "working_hours": "08:00 - 23:00",
        "location_url": "https://carlandchigatoy.taplink.ws"
    },
    {
        "name": "General Uzoqov filiali",
        "name_ru": "Филиал Генерал Узаков",
        "name_en": "General Uzoqov Branch",
        "city": "Toshkent",
        "city_ru": "Ташкент",
        "city_en": "Tashkent",
        "address": "Chimboy 2-tor ko'chasi 48",
        "address_ru": "2-й проезд Чимбой, 48",
        "address_en": "Chimboy 2nd passage 48",
        "orientr": "Orzu chorrahasidan o'tgandan keyin VISOL to'yxonasidan sal pastroqda chap qo'lda.",
        "orientr_ru": "После перекрестка Орзу чуть ниже банкетного зала VISOL слева.",
        "orientr_en": "After Orzu intersection, slightly below VISOL wedding hall on the left.",
        "working_hours": "08:00 - 23:00",
        "location_url": "https://carlandgeneraluzoqov.taplink.ws"
    },
    {
        "name": "Do'mbirobod filiali",
        "name_ru": "Филиал Домбрабад",
        "name_en": "Dombirobod Branch",
        "city": "Toshkent",
        "city_ru": "Ташкент",
        "city_en": "Tashkent",
        "address": "Dombirobod street 162",
        "address_ru": "ул. Домбрабад, 162",
        "address_en": "162 Dombirobod street",
        "orientr": "Mustang zapravkadan kirganda Grand Hotel'dan o'tib chap qo'lda; 16-shahar shifoxonasi chorrahasidan kirganda Do'mbirobod haykalidan o'tib, 2-svetofordan o'ngda.",
        "orientr_ru": "Заезд с заправки Mustang, после Grand Hotel слева; со стороны 16-й горбольницы после памятника Домбрабад со 2-го светофора направо.",
        "orientr_en": "Enter from Mustang gas station, past Grand Hotel on the left; from 16th City Hospital past Dombirobod monument, turn right at 2nd traffic light.",
        "working_hours": "08:00 - 23:00",
        "location_url": "https://carlanddombiraobod.taplink.ws"
    },
    {
        "name": "Samarqand Darvoza filiali",
        "name_ru": "Филиал Самарканд Дарвоза",
        "name_en": "Samarkand Darvoza Branch",
        "city": "Toshkent",
        "city_ru": "Ташкент",
        "city_en": "Tashkent",
        "address": "Qoratosh ko'chasi 5A",
        "address_ru": "ул. Караташ, 5А",
        "address_en": "5A Qoratosh street",
        "orientr": "Chorsudan kelishda INTRAN zapravkadan o'tgandan keyin The Chuchvara ro'parasida o'ng qo'lda.",
        "orientr_ru": "Со стороны Чорсу после заправки INTRAN, напротив The Chuchvara справа.",
        "orientr_en": "Coming from Chorsu past INTRAN gas station, opposite The Chuchvara on the right.",
        "working_hours": "08:00 - 23:00",
        "location_url": "https://carlandsamarqanddarvoza.taplink.ws"
    },
    {
        "name": "Yunusobod filiali",
        "name_ru": "Филиал Юнусабад",
        "name_en": "Yunusabad Branch",
        "city": "Toshkent",
        "city_ru": "Ташкент",
        "city_en": "Tashkent",
        "address": "Kulolqo'rg'on 6-tor ko'chasi",
        "address_ru": "6-й тупик Кулолкурган",
        "address_en": "Kulolqurgon 6th blind alley",
        "orientr": "Uchqahramon doirasidan (krug) kelganda 271-maktab ro'parasida I WASH moyka oldida chapda; Yunusobod doirasidan kelganda BYD servisdan o'tgandan keyin I WASH moyka yonida o'ng qo'lda.",
        "orientr_ru": "С круга Уч Кахрамон напротив школы №271, перед мойкой I WASH слева; с круга Юнусабад после сервиса BYD, рядом с мойкой I WASH справа.",
        "orientr_en": "From Uchqahramon roundabout opposite School #271, before I WASH car wash on the left; from Yunusabad roundabout past BYD service, next to I WASH on the right.",
        "working_hours": "08:00 - 23:00",
        "location_url": "https://carlandyunusobod.taplink.ws"
    },
    {
        "name": "Taxtapul filiali",
        "name_ru": "Филиал Тахтапуль",
        "name_en": "Takhtapul Branch",
        "city": "Toshkent",
        "city_ru": "Ташкент",
        "city_en": "Tashkent",
        "address": "Kichik halqa yo'li 74A (Ko'rgazmalar zali)",
        "address_ru": "Малая кольцевая дорога (МКАД) 74А (Выставочный зал)",
        "address_en": "Little Ring Road 74A (Exhibition Hall)",
        "orientr": "Malikadan kelganda Taxtapul ko'prikdan o'tganda o'ng qo'lda; Severniy Olmazordan kelganda Taxtapul ko'prikka yetmasdan chap qo'lda Turk Market yonida.",
        "orientr_ru": "Со стороны Малики после моста Тахтапуль справа; со стороны Северного Алмазара не доезжая моста слева, рядом с Turk Market.",
        "orientr_en": "From Malika after Takhtapul bridge on the right; from Northern Olmazor before Takhtapul bridge on the left, next to Turk Market.",
        "working_hours": "08:00 - 23:00",
        "location_url": "https://carlandtaxtapul.taplink.ws"
    },
    {
        "name": "Lunacharskiy filiali",
        "name_ru": "Филиал Луначарский",
        "name_en": "Lunacharskiy Branch",
        "city": "Toshkent",
        "city_ru": "Ташкент",
        "city_en": "Tashkent",
        "address": "Buyuk Ipak Yo'li ko'chasi 268 (Yandex)",
        "address_ru": "ул. Буюк Ипак Йули, 268",
        "address_en": "268 Buyuk Ipak Yuli street",
        "orientr": "Mirzo Ulug'bek ROVD dan o'tgandan keyin o'ng qo'lda, TTZ dan kelganda Avtoritet moykadan o'tgandan keyin Tabakani ro'parasida chap qo'lda.",
        "orientr_ru": "После Мирзо-Улугбекского РОВД справа; со стороны ТТЗ после автомойки Avtoritet, напротив кафе Табака слева.",
        "orientr_en": "Past Mirzo Ulugbek Police Dept on the right; from TTZ past Avtoritet car wash, opposite Tabaka cafe on the left.",
        "working_hours": "08:00 - 23:00",
        "location_url": "https://carlandlunacharskiy.taplink.ws"
    },
    {
        "name": "Yangibozor filiali",
        "name_ru": "Филиал Янгибазар",
        "name_en": "Yangibozor Branch",
        "city": "Toshkent viloyati",
        "city_ru": "Ташкентская область",
        "city_en": "Tashkent Region",
        "address": "Navoiy ko'chasi",
        "address_ru": "ул. Навои",
        "address_en": "Navoi street",
        "orientr": "Optim marketning ro'parasida joylashgan.",
        "orientr_ru": "Напротив супермаркета Optim market.",
        "orientr_en": "Opposite Optim Market.",
        "working_hours": "09:00 - 21:00",
        "location_url": "https://carlandyangibozor.taplink.ws"
    },
    {
        "name": "Yangiyo'l filiali",
        "name_ru": "Филиал Янгиюль",
        "name_en": "Yangiyul Branch",
        "city": "Toshkent viloyati",
        "city_ru": "Ташкентская область",
        "city_en": "Tashkent Region",
        "address": "Yangiyo'l massivi",
        "address_ru": "массив Янгиюль",
        "address_en": "Yangiyul massif",
        "orientr": "Zangiota tomonidan kelganda Massivda joylashgan; Yangiyo'l tomonidan kelganda taxta ko'prikdan o'tganda o'ng qo'lda.",
        "orientr_ru": "Со стороны Зангиота расположен в массиве; со стороны Янгиюля после деревянного моста справа.",
        "orientr_en": "From Zangiota located in the massif; from Yangiyul after the wooden bridge on the right.",
        "working_hours": "09:00 - 21:00",
        "location_url": "https://carlandyangiyol.taplink.ws"
    },
    {
        "name": "Samarqand filiali (Seliskiy)",
        "name_ru": "Филиал Самарканд (Сельский)",
        "name_en": "Samarkand Branch (Selskiy)",
        "city": "Samarqand",
        "city_ru": "Самарканд",
        "city_en": "Samarkand",
        "address": "Kovola mahallasi, 69-uy (Seliskiy tomon)",
        "address_ru": "махалля Ковола, дом 69 (сторона Сельского)",
        "address_en": "Kovola mahalla, House 69 (Selskiy side)",
        "orientr": "16-maktab orqasi, Registon ko'chasi bilan kelganda.",
        "orientr_ru": "Сзади школы №16, по улице Регистан.",
        "orientr_en": "Behind School #16, entering via Registan street.",
        "working_hours": "09:00 - 21:00",
        "location_url": "https://carlandsamarqand.taplink.ws"
    },
    {
        "name": "Buxoro filiali",
        "name_ru": "Филиал Бухара",
        "name_en": "Bukhara Branch",
        "city": "Buxoro",
        "city_ru": "Бухара",
        "city_en": "Bukhara",
        "address": "Sanoatchilar ko'chasi 3-dom",
        "address_ru": "ул. Саноатчилар, дом 3",
        "address_en": "3 Sanoatchilar street",
        "orientr": "Buxoro arxitektura texnikumi to'g'risida, 2-Lukoil zapravka yonida.",
        "orientr_ru": "Напротив Бухарского архитектурного техникума, рядом со 2-й заправкой Лукойл.",
        "orientr_en": "Opposite Bukhara Architecture College, next to 2nd Lukoil gas station.",
        "working_hours": "09:00 - 21:00",
        "location_url": "https://carlandbuxoro.taplink.ws"
    },
    {
        "name": "Index filiali (Sergeli)",
        "name_ru": "Филиал Индекс (Сергели)",
        "name_en": "Tashkent Index Branch (Sergeli)",
        "city": "Toshkent",
        "city_ru": "Ташкент",
        "city_en": "Tashkent",
        "address": "Yangihayot tumani, Sergeli Index bozori, Blok C01",
        "address_ru": "Янгихаётский район, рынок Сергели Индекс, Блок C01",
        "address_en": "Yangihayot district, Sergeli Index market, Block C01",
        "orientr": "Index bozoridan kirishda oxiriga borganda chapga qayrilasiz.",
        "orientr_ru": "При въезде на рынок Индекс проехать до конца и повернуть налево.",
        "orientr_en": "At the Index market entrance, go to the end and turn left.",
        "working_hours": "09:00 - 21:00",
        "location_url": "https://carlandtashkentindex.taplink.ws"
    },
    {
        "name": "Chirchiq filiali",
        "name_ru": "Филиал Чирчик",
        "name_en": "Chirchiq Branch",
        "city": "Toshkent viloyati",
        "city_ru": "Ташкентская область",
        "city_en": "Tashkent Region",
        "address": "10-mikrorayon",
        "address_ru": "10-й микрорайон",
        "address_en": "10th Microdistrict",
        "orientr": "Karvon bozori oldida joylashgan.",
        "orientr_ru": "Возле рынка Карвон.",
        "orientr_en": "Next to Karvon market.",
        "working_hours": "09:00 - 23:00",
        "location_url": "https://carlandchirchiq.taplink.ws"
    },
    {
        "name": "Qarshi filiali",
        "name_ru": "Филиал Карши",
        "name_en": "Karshi Branch",
        "city": "Qashqadaryo",
        "city_ru": "Кашкадарья",
        "city_en": "Kashkadarya",
        "address": "Qarshi shahri",
        "address_ru": "город Карши",
        "address_en": "Karshi city",
        "orientr": "5-hammom yaqinida, Farangiz do'konining to'g'risida.",
        "orientr_ru": "Рядом с 5-й баней, напротив магазина Фарангиз.",
        "orientr_en": "Near 5th bathhouse, opposite Farangiz store.",
        "working_hours": "09:00 - 21:00",
        "location_url": "https://carlandqarshi.taplink.ws"
    },
    {
        "name": "Olmaliq filiali",
        "name_ru": "Филиал Алмалык",
        "name_en": "Olmaliq Branch",
        "city": "Toshkent viloyati",
        "city_ru": "Ташкентская область",
        "city_en": "Tashkent Region",
        "address": "Olmaliq shahri",
        "address_ru": "город Алмалык",
        "address_en": "Olmaliq city",
        "orientr": "Olmaliq zavodiga ketishda, Hamkorbankning to'g'risida.",
        "orientr_ru": "По дороге к Алмалыкскому комбинату, напротив Хамкорбанка.",
        "orientr_en": "On the way to Olmaliq plant, opposite Hamkorbank.",
        "working_hours": "09:00 - 23:00",
        "location_url": "https://carlandolmaliq.taplink.ws"
    }
]

# Umumiy asosiy Taplink
MAIN_TAPLINK_URL = "https://carland.taplink.ws"

# Sentabr oyi Call Center maxsus aksiyalari (Paketlar)
SEPTEMBER_AKSIYALAR = {
    "paket_1_korelux": {
        "title": "🎁 PAKET-1: KORELUX X500 (5W30 / 10W40)",
        "base_price": "280 000 so'm",
        "desc": "Cobalt, Gentra, Nexia 3, Spark 1.25 uchun 280 000 so'm; Matiz, Damas, Nexia 1/2 uchun 240 000 so'm!",
        "bonuses": [
            "Havo filtri (Air filter) — BEPUL (BONUS)",
            "Salon filtri (Cabin filter) — BEPUL (BONUS)",
            "Moy filtri (Oil filter) — BEPUL (BONUS)",
            "Moy almashtirish xizmati — BEPUL"
        ]
    },
    "paket_2_hyundai_korelux700": {
        "title": "🎁 PAKET-2: HYUNDAI G700 / KORELUX X700 (5W30 / 5W40 / 10W40)",
        "base_price": "350 000 so'm",
        "desc": "Cobalt, Gentra, Nexia 3, Spark 1.25 uchun 350 000 so'm; Matiz, Damas 300 000 so'm; Captiva, Malibu, Tracker 400 000 - 500 000 so'm!",
        "bonuses": [
            "Havo filtri — BEPUL (BONUS)",
            "Salon filtri — BEPUL (BONUS)",
            "Moy filtri — BEPUL (BONUS)",
            "Moy almashtirish xizmati — BEPUL"
        ]
    },
    "paket_3_karobka_atf": {
        "title": "🎁 PAKET-3: KORELUX ATF VI / MINHO ATF VI (Karobka moyi)",
        "base_price": "750 000 so'm",
        "desc": "7.5 litr ATF VI avtomat karobka moyi (Cobalt, Gentra, Nexia 3, Captiva, Malibu, Tracker, Onix uchun)",
        "bonuses": [
            "Havo filtri — BEPUL (BONUS)",
            "Salon filtri — BEPUL (BONUS)",
            "Delfin sochiq — BEPUL (BONUS)",
            "Xushbo'ylantirgich (Osvijitel) — BEPUL (BONUS)",
            "Almashtirish xizmati — BEPUL"
        ]
    },
    "paket_5_shell_ultra": {
        "title": "🎁 PAKET-5: SHELL ULTRA AG 5W30 (Germaniya)",
        "base_price": "475 000 so'm",
        "desc": "Original nemis Shell Ultra AG moyi (Cobalt, Gentra, Nexia 3, Spark 1.25 uchun 475 000 so'm; Matiz, Damas 380 000 so'm)",
        "bonuses": [
            "Havo filtri — BEPUL (BONUS)",
            "Salon filtri — BEPUL (BONUS)",
            "Moy filtri — BEPUL (BONUS)",
            "Delfin sochiq — BEPUL (BONUS)",
            "Vita Mobile oyna suvi — BEPUL (BONUS)",
            "Almashtirish xizmati — BEPUL"
        ]
    },
    "paket_6_aveno_dexos2": {
        "title": "🎁 PAKET-6: AVENO DX2 5W30 (Germaniya)",
        "base_price": "420 000 so'm",
        "desc": "Dexos 2 sertifikatli nemis moyi (Cobalt, Gentra, Nexia 3, Spark uchun 420 000 so'm)",
        "bonuses": [
            "Havo filtri — BEPUL (BONUS)",
            "Salon filtri — BEPUL (BONUS)",
            "Moy filtri — BEPUL (BONUS)",
            "Delfin sochiq — BEPUL (BONUS)",
            "Xushbo'ylantirgich (Osvijitel) — BEPUL (BONUS)",
            "Almashtirish xizmati — BEPUL"
        ]
    },
    "lukoil_genesis_aksiya": {
        "title": "🎁 LUKOIL GENESIS UNIVERSAL 10W40 (SN/CF)",
        "base_price": "170 000 so'm",
        "desc": "Matiz, Damas va Labo uchun 3L moy bor-yo'g'i 170 000 so'm!",
        "bonuses": [
            "Moy filtri — BEPUL (BONUS)",
            "Almashtirish xizmati — BEPUL"
        ]
    }
}

# Maxsus atamalar va qoidalar (Hujjat 23-24 betlar)
SPECIAL_TERMINOLOGY = {
    "moy_filter": "Oil filter (Dvigatel moy filtri)",
    "havo_filter": "Air filter (Havo filtri)",
    "salon_filter": "Cabin filter / Lounge filter (Konditsioner/salon filtri)",
    "karobka_filter": "AKPP, АКПП, КПП filter (Avtomat/mexanika uzatmalar qutisi filtri)",
    "topliviy_filter": "Fuel filter (Yoqilg'i/benzin filtri)",
    "pampers": "ПАМПЕРС (Yoqilg'i baki ichidagi setkali filtr)",
    "kolodka": "КОЛОДКИ (Tormoz kolodkalari: Fourgreen, Hardron, Autozip, Brembo)",
    "benzanasos": "Мотор бензонасос (Yoqilg'i nasosi motori)",
    "babina": "Бабина (O't oldirish g'altagi / Zazhiganie katushkasi)"
}

# Do'konda mavjud mashhur moy brendlari va 1L narxlari (namunaviy)
POPULAR_OILS = {
    "Shell Ultra AG 5W-30 (Germaniya)": {
        "price_per_liter": 110000,
        "type": "Sintetika 5W-30",
        "desc": "Original nemis sifatidagi yuqori toifali moy"
    },
    "Castrol Magnatec / Edge 5W-30 / 5W-40": {
        "price_per_liter": 140000,
        "type": "Sintetika",
        "desc": "Dvigatelni sovuq haroratda maksimal himoyalovchi moy"
    },
    "Liqui Moly Molygen / Top Tec 5W-30 / 5W-40": {
        "price_per_liter": 160000,
        "type": "Premium Sintetika",
        "desc": "Molibden qo'shimchali, dvigatel ishqalanishini kamaytiradi"
    },
    "Valvoline SynPower 5W-30 / 0W-20 (DEXOS1)": {
        "price_per_liter": 170000,
        "type": "Sintetika Dexos1",
        "desc": "Onix, Tracker 2, Malibu 2 uchun rasmiy litsenziyali moy"
    },
    "Aveno 5W-30 Dexos 2 Excellence": {
        "price_per_liter": 120000,
        "type": "Sintetika Dexos 2",
        "desc": "Cobalt, Gentra, Lacetti, Spark uchun maxsus"
    },
    "Hyundai XTeer 5W-30 / 10W-40": {
        "price_per_liter": 90000,
        "type": "Sintetika / Yarim sintetika",
        "desc": "Koreya va xitoy avtomobillari uchun hamyonbop va sifatli"
    },
    "ZIC X7 / X9 5W-30 / 5W-40": {
        "price_per_liter": 85000,
        "type": "Sintetika",
        "desc": "Yuqori harorat barqarorligiga ega sifatli moy"
    },
    "Mannol 5W-30 / 5W-40": {
        "price_per_liter": 120000,
        "type": "Sintetika",
        "desc": "Evropa standartlariga mos moy"
    }
}

# GM Svechalar xizmat va mahsulot narxlari (Hujjat 5-bet)
GM_SVECHALAR_PRICING = {
    "Matiz": {"soni": 3, "usluga": 50000},
    "Matiz Best": {"soni": 4, "usluga": 60000},
    "Damas": {"soni": 3, "usluga": 60000},
    "Cobalt": {"soni": 4, "usluga": 80000},
    "Lacetti 1.6-1.8": {"soni": 4, "usluga": 80000},
    "Gentra": {"soni": 4, "usluga": 80000},
    "Spark 1.25": {"soni": 4, "usluga": 80000},
    "Spark 1.0": {"soni": 4, "usluga": 120000},
    "Nexia 1/2": {"soni": 4, "usluga": 80000},
    "Nexia 3": {"soni": 4, "usluga": 80000},
    "Captiva 2.4": {"soni": 4, "usluga": 100000},
    "Captiva 3.0": {"soni": 6, "usluga": 200000},
    "Malibu 1": {"soni": 4, "usluga": 80000},
    "Malibu 2": {"soni": 4, "usluga": 80000},
    "Tracker 1": {"soni": 4, "usluga": 80000},
    "Tracker 2": {"soni": 3, "usluga": 70000},
    "Onix": {"soni": 3, "usluga": 70000},
    "Trailblazer": {"soni": 6, "usluga": 200000},
    "Traverse": {"soni": 6, "usluga": 200000},
    "Equinox": {"soni": 4, "usluga": 80000},
    "Tahoe": {"soni": 8, "usluga": 300000}
}

# Aloqa va rasmiy resurslar ma'lumotlari
CARLAND_PHONE = "+998555161616"
CARLAND_PHONE_DISPLAY = "+998 55 516 16 16"
CARLAND_GENERAL_HOURS = "09:00 dan 23:00 gacha dam olish kunlarisiz"
CARLAND_WEBSITE = "https://carland.uz"
CARLAND_EMAIL = "info@carland.uz"
CARLAND_OFFICE_ADDRESS = "Toshkent shahri, Chilonzor tumani, Lutfiy ko'chasi 24A"
CARLAND_OFFICE_LOCATION = "https://yandex.uz/maps/-/CHg9bHjn"
CARLAND_APP_STORE = "https://apps.apple.com/uz/app/carland/id6746539445"
CARLAND_GOOGLE_PLAY = "https://play.google.com/store/apps/details?id=com.carland"
CARLAND_TELEGRAM_BOT = "https://t.me/carland_robot"
CARLAND_JOB_BOT = "https://t.me/carland_job_bot"
CARLAND_ONLINE_BOOKING = "https://carland.uz/ru/booking"
CARLAND_B2B_URL = "https://carland.uz/ru/pages/b2b_sale"

# Carland rasmiy avtoservis xizmatlari ro'yxati
CARLAND_OFFICIAL_SERVICES = [
    {"name": "Dvigatel (mator) moyini almashtirish", "name_ru": "Замена моторного масла", "desc": "Mator moyi xarid qilinganda almashtirish MUTLAQO BEPUL!"},
    {"name": "Avtomat va mexanika karobka moyini almashtirish", "name_ru": "Замена масла в АКПП и МКПП", "desc": "Mashina rusumiga qarab xizmat haqi olinadi. Maxsus apparatda to'liq yuvish va almashtirish."},
    {"name": "Reduktor moyini almashtirish", "name_ru": "Замена масла в редукторе", "desc": "Elektromobil va gibridlar, hamda orqa/to'liq tortuvchi avtomobillar uchun."},
    {"name": "Tormoz kolodkalarini almashtirish", "name_ru": "Замена тормозных колодок", "desc": "Fourgreen, Hardron, GM Original, Japanparts, Brake Master brendlari."},
    {"name": "Xodovoy qismini diagnostika va ta'mirlash", "name_ru": "Диагностика и ремонт ходовой части", "desc": "Podveska, amortizatorlar, richaglar va sharovoylar ko'rigi."},
    {"name": "Shinomontaj va balansirovka", "name_ru": "Шиномонтаж и балансировка колес", "desc": "Shinalar yechish-taqish, balansirovka, bosimni tekshirish."},
    {"name": "Avtoelektrik xizmati", "name_ru": "Автоэлектрик в Ташкенте", "desc": "Starter, generator, babina, datchiklar diagnostikasi va elektr ta'miri."},
    {"name": "Akkumulyator almashtirish", "name_ru": "Замена аккумулятора", "desc": "STARTER, Delkor, Bars va boshqa sifatli akkumulyatorlar."},
    {"name": "Svechalar almashtirish", "name_ru": "Замена свечей зажигания", "desc": "ACDelco GM Original, Autozip, Torch Iridium, Irizon Iridium svechalari."},
    {"name": "Benzobak va yonilg'i tizimi", "name_ru": "Ремонт бензобака и топливной системы", "desc": "Benzanasos, pampers (setka), topliviy filtrlar almashtirish."}
]


