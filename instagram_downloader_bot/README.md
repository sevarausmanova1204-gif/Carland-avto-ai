# 🤖 N28: Instagram Video Downloader & AI Assistant Bot

Instagram'dan videolarni **asl sifatda (Full HD/4K)** yuklab beruvchi hamda **Google Gemini AI** asosida video tahlili, erkin suhbat, jahon yangiliklari va ispan tili/vakansiyalar bo'yicha aqlli yordamchi Telegram bot.

---

## 🚀 Asosiy Imkoniyatlari

1. **📥 Asl sifatda Instagram video yuklash:**
   - Reels, Post, IGTV videolarni sifatini pasaytirmagan (original bitrate) holda yuklab beradi.
   - Tezkor to'g'ridan-to'g'ri CDN oqimi orqali ishlaydi (login/cookie talab qilinmaydi).
2. **🧠 Multimodal AI Video Tahlili (Google Gemini 1.5 Flash):**
   - Yuklangan video ostidagi `[ 🤖 Videoni AI bilan tahlil qilish ]` tugmasi orqali videoni to'liq tahlil qilish:
     - Asosiy mavzusi;
     - Qisqacha mazmuni;
     - Asosiy xulosalar;
     - Xorijiy tildan o'zbek tiliga tarjimasi.
3. **💬 AI Suhbatdosh:**
   - Botga istalgan mavzuda (fan, texnologiya, til, hayot) savol bering va aqlli suhbat quring.
4. **🌍 Dunyo Yangiliklari:**
   - Global siyosat, iqtisodiyot, texnologiya va jamiyatdagi eng muhim xalqaro yangiliklar dayjesti.
5. **🇪🇸 Ispan Tili, Grantlar & Vakansiyalar:**
   - Kundalik foydali so'zlar, iboralar va grammatika;
   - Ispaniya va Yevropadagi xalqaro grantlar (Erasmus, Fundación Carolina, DELE/SIELE);
   - Ispan tili bo'yicha masofaviy ishlar (remote jobs) va frilans vakansiyalari.

---

## 📁 Loyiha Tuzilmasi

```text
n28/
├── .env                # Bot tokeni va Gemini API kaliti
├── .env.example        # Namunaviy konfiguratsiya
├── requirements.txt    # Kutubxonalar (aiogram, yt-dlp, instaloader, google-generativeai)
├── config.py           # Sozlamalar va muhit o'zgaruvchilari
├── ai_service.py       # Gemini AI xizmati (video tahlil, suhbat, yangiliklar, ispan tili)
├── keyboards.py        # Reply va Inline tugmalar menyusi
├── downloader.py       # Asl sifatda yuklab olish moduli
├── handlers.py         # Telegram xabarlari, buyruqlari va callback'larni boshqarish
├── main.py             # Botni ishga tushiruvchi asosiy fayl
└── README.md           # Batafsil qo'llanma
```

---

## ⚙️ Sozlash va Ishga Tushirish

### 1. Muhit fayli (`.env`):
`.env` faylini oching va quyidagi qiymatlarni kiriting:
```env
BOT_TOKEN=sizning_bot_tokeningiz
GEMINI_API_KEY=AIzaSy...sizning_gemini_api_kalitingiz
```
> **💡 Bepul Gemini API kalit olish:** [aistudio.google.com](https://aistudio.google.com/) saytiga kiring -> **Get API key** tugmasini bosing -> Yangi kalit yarating va `.env` dagi `GEMINI_API_KEY` ga qo'ying.

### 2. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

### 3. Botni ishga tushirish:
```bash
python main.py
```

---

## 📱 Qanday Ishlatiladi?

- **/start** bosing: Asosiy qulay menyu ochiladi.
- **Instagram havola yuboring**: Video yuklanadi va ostida `[ 🤖 Videoni AI bilan tahlil qilish ]` tugmasi chiqadi.
- **🌍 Global Yangiliklar**: Jahondagi eng so'nggi yangiliklar dayjestini o'qing.
- **🇪🇸 Ispan tili & Ishlar**: Darslar, grantlar va masofaviy vakansiyalar bo'yicha ma'lumot oling.
- **Istalgan matn yozing**: AI suhbatdoshingiz siz bilan muloqot qiladi!
