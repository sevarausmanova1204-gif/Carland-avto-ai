# Carland Telegram Bot

Mashinalar uchun moy hisoblash, mahsulotlar katalogi, filiallar va AI yordamchidan
iborat Telegram bot. Ma'lumotlar bazasi Carland kompaniyasining PDF/Excel
fayllaridan avtomatik chiqarib olingan (`data/` papkasiga qarang).

## Imkoniyatlari

1. **🛢 Moy hisoblash** — mashina rusumini tanlaysiz, bot motor va
   karobka/reduktor uchun kerakli moy hajmini, tavsiya etilgan moy turini va
   ombordagi mos mahsulotlarni **narxi bilan (litriga ko'paytirilgan holda)**
   ko'rsatadi.
2. **🔧 Mahsulotlar** — havo/moy/salon/yoqilg'i filtri, avtokimyo, ehtiyot
   qismlar, akkumulyator, antifriz, svecha, shina — mashina rusumi bo'yicha
   qidiriladi.
3. **🖼 Infografika** — har bir mashina uchun motor/karobka/reduktor moy
   ma'lumotlarini ko'rsatuvchi avtomatik chiziladigan sxematik rasm (PNG).
4. **📍 Filiallar** — 15 ta filial manzili + Yandex Xaritada ochish tugmasi.
5. **🎉 Aksiyalar** — faol aksiya paketlari (Shell, Korelux, Lukoil va h.k.).
6. **💬 AI yordamchi** — Claude yoki OpenAI orqali erkin savol-javob
   (bazadagi aniq raqamlar asosida, taxmin qilib javob bermaydi).

## O'rnatish

```bash
cd carland_bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # keyin .env faylni to'ldiring
```

`.env` faylida to'ldirish kerak:

- `TELEGRAM_BOT_TOKEN` — Telegram'da [@BotFather](https://t.me/BotFather) ga
  yozib, `/newbot` orqali oling.
- `AI_PROVIDER` — `anthropic` yoki `openai`.
- `ANTHROPIC_API_KEY` — https://console.anthropic.com/settings/keys
- `OPENAI_API_KEY` — https://platform.openai.com/api-keys

## Ishga tushirish

```bash
python3 main.py
```

## Ma'lumotlar bazasini qayta yig'ish

Baza tayyor holda `data/carland.db` sifatida keladi. Agar manba fayllar
(narxlar, yangi mashina rusumlari) yangilansa:

```bash
cd data
pip install -r requirements.txt   # pymupdf, pandas, openpyxl
python3 extract_raw.py            # PDF/XLSX -> xom JSON fayllar
python3 build_database.py         # xom JSON -> carland.db
```

Yangi manba fayllarni `data/raw/` papkasiga joylashtiring va
`extract_raw.py` ichidagi fayl nomlarini moslang.

## Ma'lumotlar tuzilishi va cheklovlar (MUHIM)

Manba PDF 246 sahifadan iborat bo'lib, Excel'dan PDF'ga eksport qilingan —
bu ba'zi joylarda formatlash nomukammalliklariga olib kelgan. Quyidagilarga
e'tibor bering:

- **Moy jadvali** (83 ta asosiy qator, ba'zi ko'p-dvigatelli modellar
  variantlarga bo'lingandan keyin 92 ta): mashina rusumi, motor/karobka/
  reduktor moy hajmi, moy turi va almashtirish oralig'i **to'g'ridan-to'g'ri
  manba jadvalidan** olingan. Ba'zi yangi/elektromobil rusumlari (BYD,
  Zeekr, Voyah, Leapmotor va h.k.) uchun manba jadvalida ayrim maydonlar
  (masalan almashtirish oralig'i) bo'sh — bot bunday hollarda "ma'lumot
  yo'q" deb ko'rsatadi, taxmin qilib raqam to'qib chiqarmaydi.
- **Mahsulotlar katalogi** (3900+ dona): filtr/moy/ehtiyot qism nomlari
  katalogda **faqat mashina modeli nomi bilan** yozilgan (masalan
  "AIR FILTER ... SORENTO", "CF COBALT, MALIBU..."), marka ko'rsatilmagan.
  Bot mashina rusumidan kalit so'z (masalan "Kia Sorento" → "sorento")
  ajratib, shu so'z bo'yicha qidiradi. **Bu — aniq artikul bo'yicha emas,
  kalit so'z bo'yicha moslashtirish**, shuning uchun bot bir nechta variant
  ko'rsatadi va mosligini nomidan tekshirish tavsiya etiladi (`bot/matching.py`
  da batafsil izoh bor).
- **Antifriz**: manbada 3 ta brend (VALESCO, FELIX ROSSIYA, ZITRON — oxirgisi
  faqat qizil rangda) bir xil mashina ro'yxati bilan alohida narxlangan;
  bularning barchasi `brand` ustuni bilan alohida saqlangan.
- **Infografika**: bu haqiqiy mashina/detal fotosi EMAS — texnik
  ma'lumotlarni (hajm, moy turi) ko'rsatadigan avtomatik chiziladigan
  sxematik diagramma. Haqiqiy detal fotosi kerak bo'lsa, `assets/`
  papkasiga rasm qo'shib, `bot/infographic.py` ni shunga moslab
  o'zgartirish mumkin.
- **Yandex Xarita**: filiallar uchun aniq GPS koordinatasi manbada yo'q
  (faqat matnli yo'nalish tavsifi bor), shuning uchun bot Yandex Maps'da
  manzil bo'yicha **qidiruv havolasi** yaratadi (API kalitsiz ishlaydi).
  Aniqroq bo'lishi uchun har bir filial uchun `data/branches_structured.json`
  ga haqiqiy GPS koordinatalarini (lat/lon) qo'shish tavsiya etiladi.

## Loyiha tuzilishi

```
carland_bot/
  main.py                    # bot kirish nuqtasi
  requirements.txt
  .env.example
  bot/
    config.py                # sozlamalar (.env dan o'qiydi)
    db.py                    # SQLite so'rovlari
    matching.py               # mashina nomidan qidiruv kalit so'zi
    format.py                 # Telegram xabar matnlarini shakllantirish
    infographic.py             # PNG infografika generatori
    maps.py                    # Yandex Maps havola generatori
    ai.py                      # Claude/OpenAI integratsiyasi
    keyboards.py                # inline tugmalar
    handlers/
      start.py                 # /start
      callbacks.py              # asosiy navigatsiya
      text.py                   # qidiruv va AI erkin matn rejimi
  data/
    raw/                       # manba PDF/XLSX fayllar
    extract_raw.py              # 1-qadam: PDF/XLSX -> xom JSON
    build_database.py            # 2-qadam: xom JSON -> carland.db
    carland.db                   # yakuniy SQLite baza
    *_raw.json                   # oraliq (tekshirish/audit uchun saqlangan)
  assets/fonts/                # DejaVu Sans (ochiq litsenziyali shrift)
```
