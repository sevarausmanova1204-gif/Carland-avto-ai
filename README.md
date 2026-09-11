# 🚗 Carland AI Telegram Bot & Mashina Moylari Kalkulyatori

Carland avtoservis va do'koni uchun yaratilgan, sun'iy intellekt (**Google Gemini AI**) bilan ishlaydigan va avtomobillarga ketadigan moylarni aniq hisoblab beruvchi Telegram bot.

---

## 🌟 Asosiy Imkoniyatlari

1. **🧮 Avtomobillar uchun Moy Hisoblagich (Kalkulyator):**
   - 60 dan ortiq avtomobil modellari (Chevrolet, Kia, Hyundai, BYD, Chery, Changan, Haval, Jetour, Zeekr, Leapmotor, Dongfeng, Voyah, BMW, VW, Skoda va boshqalar);
   - Mator moyi hajmi (litrda) va tavsiya etiladigan moy turi (0w20, 5w30, 5w40, 10w40);
   - Karobka moyi hajmi va turi (Mexanika 75w90, Avtomat ATF6, CVT variator, DCT, DSG);
   - Reduktor moyi hajmi (Elektromobil va gibridlar uchun EV moylar);
   - Filtr almashtirish oralig'i (km da);
   - Do'konda mavjud mashhur moylar (Shell, Castrol, Liqui Moly, Valvoline, Aveno, XTeer, ZIC) narxlarining ko'rinishi.

2. **💬 Carland AI Maslahatchi:**
   - Carland ning 15 ta filiali manzillari, shaharlari va yo'l mo'ljallari (Toshkent, Samarqand, Buxoro, Qarshi, Chirchiq, Olmaliq va boshqalar);
   - Ehtiyot qismlar, svechalar (GM, Bosch, NGK, Torch, Irizon), filtrlar (moy, havo, salon, karobka, yonilg'i), tormoz kolodkalari (Fourgreen, Hardron, Brembo), antifriz va akkumulyatorlar bo'yicha to'liq ma'lumot;
   - Maxsus terminlar (moy filtr -> Oil filter, salon filtr -> Cabin filter, pampers, babina va h.k.);
   - Suhbat tarixini eslab qolish (kontekst) va istalgan payt tozalash (`/reset`).

3. **📱 Qulay Foydalanuvchi Interfeysi:**
   - Asosiy menyu (ReplyKeyboardMarkup): `🧮 Moy hisoblash`, `📍 Carland filiallari`, `💬 AI Maslahatchi`, `⚡ Tezkor narxlar`, `📞 Biz haqimizda & Aloqa`;
   - Interaktiv Inline menyular (Markalar -> Modellar -> Natija);
   - Matnli qidiruv (masalan: *"Cobaltga qancha moy ketadi?"*, *"BYD Song Plus matori"* deb yozsa ham avtomatik taniy oladi).

---

## 📁 Loyiha Fayllari

```text
carland_bot/
├── config.py             # Muhit o'zgaruvchilari (BOT_TOKEN, GEMINI_API_KEY)
├── car_data.py           # 60+ avtomobil texnik ma'lumotlar bazasi
├── carland_knowledge.py  # 15 ta filial, maxsus terminlar va narxlar
├── calculator.py         # Moy hisoboti formatlovchi kalkulyator
├── ai_service.py         # Google Gemini AI integratsiyasi va fallback tizimi
├── keyboards.py          # Reply va Inline tugmalar menyusi
├── handlers.py           # Telegram handlerlari (buyruqlar, xabarlar, callbacklar)
├── main.py               # Botni ishga tushiruvchi asosiy modul
├── requirements.txt      # Kutubxonalar ro'yxati
└── .env.example          # Namuna konfiguratsiya
```

---

## 🚀 Ishga Tushirish Bo'yicha Qo'llanma

### 1. Kutubxonalarni o'rnatish:
Loyiha virtual muhiti (`venv`) orqali:
```bash
source ../venv/bin/activate
pip install -r requirements.txt
```

### 2. Sozlash (`.env`):
`.env` faylida quyidagi kalitlar to'ldirilgan bo'lishi kerak:
```env
BOT_TOKEN=sizning_bot_tokeningiz
GEMINI_API_KEY=AIzaSy...sizning_gemini_api_kalitingiz
```
*(Agar asosiy `n28/.env` faylida ushbu kalitlar allaqachon mavjud bo'lsa, bot avtomatik ravishda ulardan foydalanadi).*

### 3. Botni ishga tushirish:
```bash
python3 main.py
```
yoki venv orqali:
```bash
../venv/bin/python3 main.py
```
