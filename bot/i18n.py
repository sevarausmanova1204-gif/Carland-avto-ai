"""Oddiy ikki tilli (o'zbek/rus) matnlar lug'ati.

Eslatma: bu bot ASOSIY menyusi va sarlavhalarini tarjima qiladi.
Batafsil natija matnlari (moy hisobi, mahsulot ro'yxatlari va h.k.)
`bot/format.py` ichida alohida, `lang` parametriga qarab tarjima qilinadi.
Faqat mahsulot nomlari (baza qiymatlari — ko'pincha ruscha/inglizcha
aralash yozilgan) tarjima qilinmaydi, chunki ular katalogdagi tayyor
matn sifatida saqlanadi.
"""

TEXT = {
    "welcome": {
        "uz": (
            "👋 *Carland botiga xush kelibsiz!*\n\n"
            "Mashina rusumini yozing — bot darhol aytadi:\n"
            "🛢 qaysi moy va necha litr kerak, narxi qancha\n"
            "🔧 filtr, antifriz, akkumulyator, shina — mosini topadi\n"
            "🎁 joriy aksiyalar va bonus sovg'alar\n"
            "📍 eng yaqin filial va lokatsiya\n\n"
            "✍️ Masalan yozing: *Cobalt moyi* yoki *moy filtri Nexia 3*\n\n"
            "💳 *5% KESHBEK*: Carland mobil ilovasini yuklab oling — birinchi xaridingizga 5% keshbek qaytadi.\n\n"
            "Quyidagi menyudan boshlang 👇"
        ),
        "ru": (
            "👋 *Добро пожаловать в бот Carland!*\n\n"
            "Напишите модель автомобиля — бот сразу подскажет:\n"
            "🛢 какое масло и сколько литров нужно, и цену\n"
            "🔧 фильтры, антифриз, аккумулятор, шины — подберёт подходящее\n"
            "🎁 текущие акции и бонусные подарки\n"
            "📍 ближайший филиал и локацию\n\n"
            "✍️ Например, напишите: *Cobalt масло* или *масляный фильтр Nexia 3*\n\n"
            "💳 *КЕШБЭК 5%*: скачайте мобильное приложение Carland — на первую покупку вернём 5% кешбэка.\n\n"
            "Начните с меню ниже 👇"
        ),
    },
    "menu_app_ios": {"uz": "📱 iPhone — 5% keshbek", "ru": "📱 iPhone — кешбэк 5%"},
    "menu_app_android": {"uz": "🤖 Android — 5% keshbek", "ru": "🤖 Android — кешбэк 5%"},
    "cashback_note": {
        "uz": "💳 *5% keshbek*: Carland mobil ilovasini yuklab oling — birinchi xaridingizga 5% keshbek qaytadi.",
        "ru": "💳 *Кешбэк 5%*: скачайте мобильное приложение Carland — на первую покупку вернём 5%.",
    },
    "main_menu_title": {"uz": "Bosh menyu:", "ru": "Главное меню:"},
    "menu_oilcalc": {"uz": "🛢 Moy hisoblash", "ru": "🛢 Расчёт масла"},
    "menu_products": {"uz": "🔧 Mahsulotlar", "ru": "🔧 Товары"},
    "menu_info": {"uz": "🖼 Infografika (motor/karobka/reduktor)", "ru": "🖼 Инфографика (двигатель/КПП/редуктор)"},
    "menu_branches": {"uz": "📍 Filiallar", "ru": "📍 Филиалы"},
    "menu_promo": {"uz": "🎉 Aksiyalar", "ru": "🎉 Акции"},
    "promo_hub_title": {
        "uz": "🎉 *Aksiyalar* — nimani ko'rmoqchisiz?\n\n💳 *5% keshbek*: Carland ilovasini yuklab oling — birinchi xaridga 5% qaytadi.",
        "ru": "🎉 *Акции* — что показать?\n\n💳 *Кешбэк 5%*: скачайте приложение Carland — на первую покупку вернём 5%.",
    },
    "promo_posters_btn": {"uz": "🗓 Joriy aksiyalar (rasmda)", "ru": "🗓 Текущие акции (картинками)"},
    "promo_by_car_btn": {"uz": "🚗 Mashina bo'yicha", "ru": "🚗 По автомобилю"},
    "promo_posters_caption": {
        "uz": "🎉 *Oktabr aksiyalari* — {n} ta paket, {deadline}.\n🎁 Har bir rasmda bonus sovg'alar alohida ko'rsatilgan.\n💳 Ilovani yuklab oling — birinchi xaridga *5% keshbek*:\n📱 iPhone: {app}\n🤖 Android: {play}\nMashinangizga mos paketni ko'rish uchun «🚗 Mashina bo'yicha» ni bosing.",
        "ru": "🎉 *Акции октября* — {n} пакетов, {deadline}.\n🎁 Бонусные подарки на каждой картинке показаны отдельно.\n💳 Скачайте приложение — *кешбэк 5%* на первую покупку:\n📱 iPhone: {app}\n🤖 Android: {play}\nЧтобы увидеть пакеты для вашего авто, нажмите «🚗 По автомобилю».",
    },
    "promo_none": {
        "uz": "Hozircha faol aksiya yo'q. Yangi aksiyalar e'lon qilinganda shu yerda chiqadi.",
        "ru": "Сейчас активных акций нет. Новые акции появятся здесь.",
    },
    "promo_car_posters_note": {
        "uz": "🖼 {model} uchun mos aksiya paketlari rasmda:",
        "ru": "🖼 Подходящие акционные пакеты для {model}:",
    },
    "menu_ai": {"uz": "💬 AI yordamchidan so'rash", "ru": "💬 Спросить AI-помощника"},
    "menu_recent": {"uz": "🕐 So'nggi ko'rilgan mashinalar", "ru": "🕐 Недавно просмотренные"},
    "recent_title": {"uz": "🕐 So'nggi ko'rilgan mashinalaringiz:", "ru": "🕐 Недавно просмотренные автомобили:"},
    "recent_empty": {
        "uz": "Hali birorta mashina ko'rilmagan. Avval \"🛢 Moy hisoblash\" yoki boshqa bo'limdan mashina tanlang — u shu yerda saqlanadi.",
        "ru": "Вы ещё не просматривали ни один автомобиль. Выберите машину в разделе \"🛢 Расчёт масла\" или другом — она появится здесь.",
    },
    "menu_admin": {"uz": "📞 Admin bilan bog'lanish", "ru": "📞 Связаться с админом"},
    "menu_lang": {"uz": "🌐 Til / Язык", "ru": "🌐 Til / Язык"},
    "lang_pick": {"uz": "Tilni tanlang:", "ru": "Выберите язык:"},
    "lang_saved": {"uz": "✅ Til o'zbekchaga o'rnatildi.", "ru": "✅ Язык изменён на русский."},
    # Navigatsiya ekranlari (marka/mashina tanlash, orqaga/bosh menyu tugmalari)
    "oilcalc_pick_brand": {
        "uz": "🛢 Moy hisoblash — avval mashina markasini tanlang:",
        "ru": "🛢 Расчёт масла — сначала выберите марку автомобиля:",
    },
    "info_pick_brand": {
        "uz": "🖼 Infografika — avval mashina markasini tanlang:",
        "ru": "🖼 Инфографика — сначала выберите марку автомобиля:",
    },
    "promo_pick_brand": {
        "uz": "🎉 Aksiya — avval mashina markasini tanlang:",
        "ru": "🎉 Акция — сначала выберите марку автомобиля:",
    },
    "pick_brand": {"uz": "Avval mashina markasini tanlang:", "ru": "Сначала выберите марку автомобиля:"},
    "choose_car_suffix": {"uz": "mashinani tanlang:", "ru": "выберите автомобиль:"},
    "products_menu_title": {"uz": "Qaysi mahsulot turi kerak?", "ru": "Какой тип товара нужен?"},
    "branches_pick_title": {"uz": "Filiallardan birini tanlang:", "ru": "Выберите один из филиалов:"},
    "ai_mode_on": {
        "uz": "💬 AI yordamchi rejimi yoqildi.\nSavolingizni yozing (masalan: \"Cobalt uchun qaysi moy yaxshiroq?\").",
        "ru": "💬 Режим AI-помощника включён.\nНапишите ваш вопрос (например: \"Какое масло лучше для Cobalt?\").",
    },
    "search_car_name_prompt": {
        "uz": "🔎 Mashina nomini yozing (masalan: Cobalt, Sorento, Nexia 3):",
        "ru": "🔎 Напишите название автомобиля (например: Cobalt, Sorento, Nexia 3):",
    },
    "search_oil_name_prompt": {
        "uz": "🔎 Moy nomini yoki brendini yozing (masalan: Valvoline, Castrol, Mobil):",
        "ru": "🔎 Напишите название или бренд масла (например: Valvoline, Castrol, Mobil):",
    },
    "car_not_found": {"uz": "Mashina topilmadi.", "ru": "Автомобиль не найден."},
    "search_by_name_btn": {"uz": "🔎 Nomi bo'yicha qidirish", "ru": "🔎 Поиск по названию"},
    "back_home_btn": {"uz": "⬅️ Bosh menyu", "ru": "⬅️ Главное меню"},
    "home_btn": {"uz": "🏠 Bosh menyu", "ru": "🏠 Главное меню"},
    "back_to_brands_btn": {"uz": "⬅️ Markalar", "ru": "⬅️ Марки"},
    "back_btn": {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад"},
    "back_products_menu_btn": {"uz": "⬅️ Mahsulotlar menyusi", "ru": "⬅️ Меню товаров"},
    "home_products_menu_btn": {"uz": "🏠 Mahsulotlar menyusi", "ru": "🏠 Меню товаров"},
    "back_country_select_btn": {"uz": "⬅️ Davlat tanlash", "ru": "⬅️ Выбор страны"},
    "motor_oil_prices_btn": {"uz": "🛢 Motor moyi narxlari", "ru": "🛢 Цены на моторное масло"},
    "gearbox_oil_prices_btn": {"uz": "⚙️ Karobka/reduktor moyi narxlari", "ru": "⚙️ Цены на масло КПП/редуктора"},
    "back_to_list_btn": {"uz": "⬅️ Ro'yxatga qaytish", "ru": "⬅️ Вернуться к списку"},
    "search_oil_by_name_btn": {"uz": "🔎 Moy nomi bo'yicha qidirish", "ru": "🔎 Поиск масла по названию"},
    "unknown_category": {"uz": "Noma'lum kategoriya.", "ru": "Неизвестная категория."},
    "infographic_preparing": {"uz": "🖼 {model} uchun infografika tayyorlanmoqda...", "ru": "🖼 Готовим инфографику для {model}..."},
    "infographic_caption": {"uz": "🚗 {model} — motor / karobka / reduktor sxemasi", "ru": "🚗 {model} — схема двигателя / КПП / редуктора"},
    "infographic_multi_note": {"uz": "⬆️ {model} uchun {n} ta infografika (dvigatel variantlari)", "ru": "⬆️ {n} инфографики для {model} (варианты двигателя)"},
    "no_engine_liters": {"uz": "Bu model uchun motor moyi hajmi bazada ko'rsatilmagan.", "ru": "Объём моторного масла для этой модели не указан в базе."},
    "no_gearbox_data": {"uz": "⚙️ *Karobka moyi*: bu mashina rusumida karobka qismi mavjud emas yoki bazada ma'lumot yo'q.", "ru": "⚙️ *Масло КПП*: у этой модели нет КПП, либо данных в базе нет."},
    "no_reductor_data": {"uz": "🛞 *Reduktor moyi*: bu mashina rusumida reduktor qismi mavjud emas yoki bazada ma'lumot yo'q.", "ru": "🛞 *Масло редуктора*: у этой модели нет редуктора, либо данных в базе нет."},
    "search_no_results": {
        "uz": "Hech narsa topilmadi. Qayta urinib ko'ring yoki menyudan tanlang.",
        "ru": "Ничего не найдено. Попробуйте ещё раз или выберите из меню.",
    },
    "search_results_title": {"uz": "Topilgan natijalar:", "ru": "Найденные результаты:"},
    "ai_thinking": {"uz": "💭 O'ylayapman...", "ru": "💭 Думаю..."},
    "ai_error": {
        "uz": "😔 AI xizmatida vaqtincha xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring.",
        "ru": "😔 Временная ошибка в работе AI. Попробуйте ещё раз чуть позже.",
    },
    "send_location_btn": {"uz": "📍 Lokatsiyani yuborish", "ru": "📍 Отправить локацию"},
    "open_yandex_maps_btn": {"uz": "🗺 Yandex Xaritada ochish", "ru": "🗺 Открыть в Яндекс Картах"},
    "back_to_branches_list_btn": {"uz": "⬅️ Filiallar", "ru": "⬅️ Филиалы"},
    "europe_brands_btn": {"uz": "🇪🇺 Yevropa brendlari", "ru": "🇪🇺 Европейские бренды"},
    "other_countries_btn": {"uz": "🌏 Boshqa davlatlar", "ru": "🌏 Другие страны"},
    "select_origin_suffix": {"uz": "davlat kelib chiqishini tanlang:", "ru": "выберите страну происхождения:"},
    "origin_europe_label": {"uz": "Yevropa", "ru": "Европа"},
    "origin_other_label": {"uz": "Boshqa davlatlar", "ru": "Другие страны"},
    "motor_oil_title": {"uz": "🛢 Motor moyi", "ru": "🛢 Моторное масло"},
    "gearbox_oil_title": {"uz": "⚙️ Karobka moyi", "ru": "⚙️ Масло КПП"},
    "reductor_oil_title": {"uz": "🛞 Reduktor moyi", "ru": "🛞 Масло редуктора"},
    "legacy_keyboard_note": {
        "uz": "✅ Menyu yangilandi — endi shu tugmalardan foydalaning:",
        "ru": "✅ Меню обновлено — используйте эти кнопки:",
    },
    "about_text": {
        "uz": "🏢 *Carland* — avtomobil moylari, filtrlari va ehtiyot qismlari do'koni.\n\nSavol yoki taklifingiz bo'lsa, administrator bilan bog'laning:",
        "ru": "🏢 *Carland* — магазин автомасел, фильтров и запчастей.\n\nЕсли у вас есть вопрос или предложение, свяжитесь с администратором:",
    },
    "cleared_text": {
        "uz": "🧹 Suhbat tarixi tozalandi. Yangidan boshlashingiz mumkin.",
        "ru": "🧹 История диалога очищена. Можете начать заново.",
    },
}


def t(key: str, lang: str = "uz") -> str:
    entry = TEXT.get(key, {})
    return entry.get(lang, entry.get("uz", key))
