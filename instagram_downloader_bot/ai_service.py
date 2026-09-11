import asyncio
import logging
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

from config import GEMINI_API_KEY, OPENAI_API_KEY

logger = logging.getLogger(__name__)

# OpenAI Client
_openai_client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=OPENAI_API_KEY, timeout=15.0)
    except Exception as e:
        logger.error(f"OpenAI client yuklashda xatolik: {e}")

# Gemini Client
_gemini_available = bool(GEMINI_API_KEY and len(GEMINI_API_KEY) > 10)
if _gemini_available:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Gemini sozlashda xatolik: {e}")
        _gemini_available = False

# Foydalanuvchilarning suhbat tarixi (User ID -> List[Dict])
_user_histories: Dict[int, List[Dict[str, str]]] = {}

# Video tahlil uchun vaqtinchalik ma'lumotlar kesh (video_id -> dict)
_video_cache: Dict[str, Dict[str, Any]] = {}

SYSTEM_INSTRUCTION = """
Sen N28 botining professional, chuqur bilimga ega va faktlarga asoslangan shaxsiy aqlli ekspertisan.

QAT'IY QOIDALAR VA STANDARTLAR:
1. UMUMIY VA MAVHUM GAPLAR QAT'IYAN TAQIQLANADI. "Ispaniya chiroyli mamlakat", "turli shaharlar bor", "ko'p o'rganish kerak" kabi quruq gaplar yozma.
2. FAQAT ANIQ FAKTLAR VA RAQAMLAR BER:
   - Aniq yevro narxlari (ijara, oziq-ovqat, transport, maoshlar);
   - Aniq qonunlar, vizalar (Arraigo Social, Digital Nomad Visa 2,646€);
   - Aniq foizlar va statistika (masalan, 500 ta eng faol so'z 78% nutqni tashkil qiladi);
   - Real dasturlar va platformalar nomi (Idealista, Mercadona, ProZ, Dreaming Spanish);
   - Ispan tilidagi real jonli jumlalar, grammatik formulalar va talaffuz qoidalari.
3. JAVOBLAR IXCHAM, LO'NDA, STRUKTURALANGAN VA O'QISHGA QULAY BO'LSIN (punktlar, emojilar, qalin shrift).
"""

# ==============================================================================
# ANIQ, ISBOTLANGAN VA BOY FAKTIK DOSYE (0.01 soniyada tezkor yetkazish uchun)
# ==============================================================================
FACT_DOSSIERS = {
    'culture': (
        "🇪🇸 **ISPANIYA URF-ODATLARI VA UDAMLARI: ANIQ FAKTLAR**\n\n"
        "1. ☕️ **La Sobremesa (Dasturxon suhbati):**\n"
        "• Ispanlar tushlik yoki kechki ovqat tugagach, darhol o'rnidan turmaydi. 45-90 daqiqa davomida stol atrofida qahva (*café cortado*) yoki desert ustida suhbatlashish majburiy etiket hisoblanadi.\n\n"
        "2. 💤 **Siesta (Kunduzgi orom):**\n"
        "• Haqiqat: Ispanlarning faqat 18% i kunduzi uxlaydi. Lekin soat 14:00 dan 17:00 gacha kichik do'konlar (*comercio local*), dorixonalar va davlat banklari (banklar 14:00 da yopiladi!) to'liq tanaffusga chiqadi.\n\n"
        "3. 💋 **Dos Besos (Ikki yanoqdan o'pish):**\n"
        "• Salomlashishda avval o'ng, keyin chap yanoq tekkiziladi (haqiqiy o'pish emas, havoiy ovoz chiqariladi). Erkak-ayol va ayol-ayol birinchi uchrashuvdayoq shunday salomlashadi. Erkaklar esa faqat qo'l siqishadi yoki quchoqlashadi (*abrazo*).\n\n"
        "4. 🗣 **Tuteo (Rasmiyatchilikning yo'qligi):**\n"
        "• Ispaniyada 'Siz' (*Usted*) deyarli ishlatilmaydi (faqat 75+ yoshli qariyalarga). Do'konda, universitetda professordan tortib ishda direktorgacha barcha 'Sen' (*Tú*) deb erkin muloqot qiladi.\n\n"
        "5. 🍇 **Las 12 Uvas de la Suerte (Yangi yilda 12 ta uzum):**\n"
        "• 31-dekabr yarim tunda Madridning *Puerta del Sol* maydonidagi soat har bong urganida (har 3 soniyada) bittadan jami 12 ta uzum yeyiladi. 12 ta uzumni yeb ulgurgan odamning yangi yildagi 12 oyi baxtli o'tadi deb ishoniladi.\n\n"
        "6. 🍅 **Asosiy Festivallar:**\n"
        "• **La Tomatina:** Har avgustning oxirgi chorshanbasida Bunyol shahrida 150 tonna pomidor sochiladi;\n"
        "• **Las Fallas (Valensiya):** 15-19 mart kunlari 700 dan ortiq ulkan satirik haykallar ko'chalarda yoqib yuboriladi (*La Cremà*)."
    ),

    'lifestyle': (
        "🏖 **ISPANIYADA YASHASH VA XARAJATLAR: ANIQ RAQAMLAR (2024-2025)**\n\n"
        "💶 **1. Oylik yashash xarajatlari:**\n"
        "• **Ijara (1 xonali kvartira):**\n"
        "  - Madrid & Barselona: 900€ – 1,300€/oy (xona: 400€ - 550€)\n"
        "  - Valensiya & Sevilla: 650€ – 850€/oy (xona: 280€ - 380€)\n"
        "  - Granada & Alikante: 500€ – 700€/oy (Granada — eng arzon talabalar shahri!)\n"
        "• **Oziq-ovqat (Mercadona, Lidl, Carrefour):** 1 kishi uchun oyiga 180€ – 240€;\n"
        "• **Kommunal to'lovlar (suv, elektr, gaz, wifi):** Oyiga 110€ – 150€;\n"
        "• **Jamoat transporti:** Madridda *Abono Joven* (26 yoshgacha) oyiga 8€ – 20€, kattalarga 21.80€ – 54€.\n\n"
        "💰 **2. Minimal va o'rtacha maosh:**\n"
        "• Qonuniy minimal ish haqi (**SMI**): 1,134€ (14 ta oylik) yoki oyiga 1,323€ (12 oyga);\n"
        "• O'rtacha oylik maosh: 1,850€ – 2,200€ (soliqlar chegirilgach).\n\n"
        "⏰ **3. Kun tartibi va ish vaqti:**\n"
        "• Tushlik vaqti: 14:00 – 15:30 (Ispanlar hech qachon 12:00 da tushlik qilmaydi);\n"
        "• Kechki ovqat: 21:30 – 23:00. Restoranlar 16:30 dan 20:30 gacha ovqat bermaydi, oshxona yopiq bo'ladi!\n\n"
        "⚖️ **4. Qonuniylashish va viza imkoniyatlari:**\n"
        "• **Arraigo Social:** Ispaniyada 3 yil nolegal yashab, 1 yillik ish taklifi bilan qonuniy rezidensiya olish mumkin;\n"
        "• **Digital Nomad Visa:** Masofaviy ishlovchilar uchun (oylik daromad kamida 2,646€ bo'lishi shart);\n"
        "• **Talabalik vizasi (*Estancia por estudios*):** Haftasiga 30 soatgacha rasmiy ishlash huquqini beradi."
    ),

    'speed_learning': (
        "⚡️ **ISPAN TILINI TEZ O'RGANISH SIRLARI (A1 -> B2 ANIQ METODIKA)**\n\n"
        "📊 **1. Pareto (80/20) qoidasi:**\n"
        "• *Real Academia Española (RAE)* tadqiqotiga ko'ra, eng faol **500 ta so'z** og'zaki muloqotning **78.4%** ini tashkil qiladi! 1,000 ta so'z esa barcha kitob va filmlarning 88% ini tushunishga yetadi.\n\n"
        "🧠 **2. Fe'llarni yodlashdagi 2 ta eng katta lifehack:**\n"
        "• **1-Lifehack (Kelasi zamon formulasi):** Ispancha 10 xil kelasi zamon qo'shimchalarini yodlamang! Shunchaki **'Ir + a + fe'l'** dan foydalaning:\n"
        "  - *Voy a comer* (Ovqatlanmoqchiman / ovqatlanaman)\n"
        "  - *Vamos a hablar* (Gaplashamiz)\n"
        "• **2-Lifehack (O'tgan zamon):** *Pretérito Perfecto* dan foydalaning: **'He / Has / Ha + fe'l(-ado/-ido)'**:\n"
        "  - *He comprado* (Sotib oldim), *He visto* (Ko'rdim).\n\n"
        "🎧 **3. 'Comprehensible Input' (Stephen Krashen ilmiy metodi):**\n"
        "• Grammatika qoidalarini yodlab bosh qotirmang. Kuniga 20 daqiqa YouTube'dagi **'Dreaming Spanish' (Superbeginner)** kanalini ko'ring. So'zlarni tarjimasiz, imo-ishora orqali miyangiz boladek qabul qiladi.\n\n"
        "🗣 **4. Shadowing (Talaffuz mashqi):**\n"
        "• 'Hoy Hablamos' podcastining 1 daqiqasini oling. Diktor gapirishi bilan bir vaqtda orqasidan intonatsiyasigacha baland ovozda takrorlang (kuniga 10 daqiqa).\n\n"
        "⚠️ **5. Eng ko'p qilinadigan 2 ta xato:**\n"
        "• *SER* (doimiy mohiyat: *Soy uzbeko*, *Es profesor*) vs *ESTAR* (vaqtinchalik holat: *Estoy cansado*, *Está en Madrid*);\n"
        "• *POR* (sabab: *gracias por venir*) vs *PARA* (maqsad: *este regalo es para ti*)."
    ),

    'jobs_grants': (
        "💼 **GRANTLAR, TA'LIM VA ISPAN TILI VAKANSIYALARI: ANIQ FAKTLAR**\n\n"
        "🎓 **1. 100% Lik Grant Dasturlari:**\n"
        "• **Fundación Carolina:** Magistratura va doktorantura uchun eng nufuzli grant. To'liq kontrakt (100%), oylik 750€ – 900€ stipendiya, samolyot chiptasi va sug'urta qoplanadi. (Ariza qabuli: har yili yanvar – mart oylarida);\n"
        "• **Erasmus Mundus:** Oylik 1,400€ to'liq stipendiya va tekin ta'lim;\n"
        "• **Davlat universitetlari to'lovi:** Ispaniyada Yevropa fuqarosi bo'lmaganlar uchun ham kontrakt yiliga atigi **1,200€ – 3,500€** atrofida (Buyuk Britaniya yoki AQShdan 10 barobar arzon!).\n\n"
        "📜 **2. Talab qilinadigan sertifikatlar:**\n"
        "• O'qish va ishga kirish uchun **DELE B2** yoki **SIELE Global (kamida 700 ball)** talab etiladi. SIELE imtihonini kompyuterda topshirish mumkin va natijasi 3 kunda chiqadi.\n\n"
        "💼 **3. Ispan tili bo'yicha masofaviy ishlar (Remote Jobs):**\n"
        "• **Tarjimonlik (ProZ.com, TranslatorsCafe):** 1 so'z uchun stavka 0.05$ – 0.09$ (oylik 800$ – 1,800$ topsa bo'ladi);\n"
        "• **Customer Support & Virtual Assistant:** Teleperformance, Concentrix, BairesDev kompaniyalari ispan tili biluvchilarga masofadan oyiga **900$ – 1,500$** to'laydi;\n"
        "• **Vakansiya qidirish platformalari:** *InfoJobs.net* (Ispaniyadagi #1 ish sayti), *LinkedIn Jobs*, *RemoteOK*."
    ),

    'learning': (
        "📚 **ISPANLAR HAR KUNI ISHLATADIGAN 5 TA HAQIQIY JONLI IBORA**\n\n"
        "1. 🇪🇸 **¡Qué guay! / ¡Mola mucho!** [Ke guay / Mola mucho]\n"
        "• *Ma'nosi:* Juda zo'r! Daxshat! Ajoyib!\n"
        "• *Misol:* *Esta película mola mucho.* (Bu kino juda zo'r ekan).\n\n"
        "2. 🇪🇸 **Tomar el pelo** [Tomar el pelo]\n"
        "• *Ma'nosi:* Hazillashmoq, laqillatmoq (so'zma-so'z: sochini ushlamoq).\n"
        "• *Misol:* *¿Me estás tomando el pelo?* (Meni laqillatyapsanmi?)\n\n"
        "3. 🇪🇸 **Estar sin blanca** [Estar sin blanka]\n"
        "• *Ma'nosi:* Bir tiyinsiz qolmoq, cho'ntak quruq bo'lmoq.\n"
        "• *Misol:* *No puedo ir al cine, estoy sin blanca.* (Kinoga borolmayman, pulsizman).\n\n"
        "4. 🇪🇸 **Estar como una cabra** [Estar komo una kabra]\n"
        "• *Ma'nosi:* Jinniroq, tentaknamo bo'lmoq (so'zma-so'z: echkiga o'xshamoq).\n"
        "• *Misol:* *Ese chico está como una cabra.* (U bola rosa tentakroq ekan).\n\n"
        "5. 🇪🇸 **No pasa nada / Vale** [No pasa nada / Bale]\n"
        "• *Ma'nosi:* Hech qisi yo'q / Mayli, tushunarli, kelishdik.\n"
        "• *Misol:* *¿Quedamos a las ocho? — Vale.* (Soat sakkizda uchrashamizmi? — Kelishdik)."
    ),

    'resources': (
        "🎧 **ISPAN TILINI MUSTAQIL O'RGANISH UCHUN ENG SARA RESURSLAR**\n\n"
        "1. 📺 **Eng foydali YouTube kanallar:**\n"
        "• **Dreaming Spanish:** Boshlovchilar uchun dunyodagi eng yaxshi kanal (so'zlarni imo-ishoralar bilan o'rgatadi);\n"
        "• **Butterfly Spanish:** Grammatikani eng oson va kulgili tushuntiradigan kanal;\n"
        "• **Extra en Español (Serial):** Maxsus til o'rganuvchilar uchun yaratilgan 13 qismli qiziqarli komedik serial.\n\n"
        "2. 🎙 **Eng yaxshi podcastlar (Spotify / Apple Podcasts):**\n"
        "• **Coffee Break Spanish:** Noldan boshlovchilar uchun;\n"
        "• **Hoy Hablamos:** Kundalik 10 daqiqalik qiziqarli tushunarli ispancha podcast;\n"
        "• **Radio Ambulante:** B2-C1 darajadagi Lotin Amerikasi hikoyalari.\n\n"
        "3. 📱 **Eng foydali bepul ilovalar:**\n"
        "• **Anki:** Interval takrorlash orqali so'zlarni bir umrga eslab qolish uchun;\n"
        "• **Tandem / HelloTalk:** Haqiqiy ispanlar bilan bepul yozishib, gaplashib til amaliyoti qilish;\n"
        "• **SpanishDict:** Dunyodagi eng zo'r ispancha lug'at va konjugatsiya platformasi."
    )
}


def is_ai_configured() -> bool:
    """AI xizmatlaridan (OpenAI yoki Gemini) kamida bittasi sozlanganligini tekshirish."""
    return bool(_openai_client is not None or _gemini_available)


def save_video_to_cache(cache_id: str, data: Dict[str, Any]) -> None:
    """Videoni AI tahlili uchun keshda saqlash."""
    data['cached_at'] = time.time()
    _video_cache[cache_id] = data

    # 30 daqiqadan eski kesh elementlarini tozalash
    now = time.time()
    expired_keys = [k for k, v in _video_cache.items() if now - v.get('cached_at', 0) > 1800]
    for k in expired_keys:
        _video_cache.pop(k, None)


def get_cached_video(cache_id: str) -> Optional[Dict[str, Any]]:
    """Keshdagi video ma'lumotlarini olish."""
    return _video_cache.get(cache_id)


def _generate_fast_facts(prompt: str, system_override: Optional[str] = None, max_tokens: int = 700) -> str:
    """
    OpenAI (gpt-4o-mini) orqali juda tez (2 soniyada) va aniq faktlar bilan javob olish.
    """
    sys_instruction = system_override or SYSTEM_INSTRUCTION

    # 1. OpenAI (gpt-4o-mini, past temperature=0.25 aniq faktlar uchun)
    if _openai_client:
        try:
            resp = _openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.25,
                max_tokens=max_tokens
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI xatosi: {e}. Gemini sinab ko'riladi...")

    # 2. Gemini fallback
    if _gemini_available:
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(
                model_name="gemini-3.6-flash",
                system_instruction=sys_instruction
            )
            resp = model.generate_content(prompt)
            return resp.text.strip()
        except Exception as e:
            logger.error(f"Gemini xatosi: {e}")
            raise

    raise RuntimeError("AI xizmatiga ulanib bo'lmadi.")


def _sync_analyze_video(video_path: Optional[str], caption: str, owner: Optional[str]) -> str:
    """
    Video faylini yoki uning matnini tahlil qilish.
    """
    if not is_ai_configured():
        return (
            "⚠️ **AI xizmati faollashtirilmagan.**\n\n"
            "Videoni tahlil qilish uchun API kalit kiritilishi kerak."
        )

    prompt = (
        "Sen professional video tahlilchisisan. Quyidagi Instagram video haqidagi ma'lumotlarni "
        "sinchkovlik bilan o'rganib chiq va o'zbek tilida juda chiroyli va tushunarli tahlil taqdim et.\n\n"
        f"Video muallifi: @{owner if owner else 'Noma`lum'}\n"
        f"Video izohi/matni: {caption}\n\n"
        "Quyidagi struktura bo'yicha aniq faktlar bilan javob ber:\n"
        "🎯 **Asosiy mavzusi:** (Video nima haqida)\n"
        "📝 **Qisqacha mazmuni:** (Videoda nimalar aytildi yoki ko'rsatildi)\n"
        "💡 **Asosiy xulosalar va foydali fikrlar:** (Tomoshabin uchun nima foydali)\n"
        "🌐 **Til va tarjima:** (Videodagi til va o'zbek tiliga tarjima/izoh)\n"
        "🌟 **Ekspert maslahati / Fikr:** (Ushbu mavzu bo'yicha qisqa tavsiya)"
    )

    # Agar Gemini mavjud bo'lsa va mahalliy fayl bor bo'lsa, faylni yuklab tahlil qilamiz
    if _gemini_available and video_path and Path(video_path).exists():
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(
                model_name="gemini-3.6-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            uploaded_file = genai.upload_file(video_path)
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)

            if uploaded_file.state.name == "ACTIVE":
                resp = model.generate_content([uploaded_file, prompt])
                try:
                    uploaded_file.delete()
                except Exception:
                    pass
                return resp.text.strip()
        except Exception as e:
            logger.warning(f"Gemini video upload xatosi: {e}. Matnli AI tahliliga o'tiladi.")

    # Matn va kontekst bo'yicha OpenAI orqali tahlil
    try:
        return _generate_fast_facts(prompt, max_tokens=700)
    except Exception as e:
        logger.error(f"Video tahlil qilishda xatolik: {e}", exc_info=True)
        return f"❌ Videoni tahlil qilishda xatolik yuz berdi: {e}"


async def analyze_video(video_path: Optional[str], caption: str, owner: Optional[str]) -> str:
    """Asinxron video tahlil chaqiruvi."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_analyze_video, video_path, caption, owner)


def _sync_chat(user_id: int, message_text: str) -> str:
    """AI bilan tezkor va faktlarga boy erkin suhbatlashish."""
    if not is_ai_configured():
        return (
            "⚠️ **AI xizmati sozlanmagan.**\n\n"
            "AI bilan suhbatlashish uchun `.env` fayliga API kalit kiritilgan bo'lishi kerak."
        )

    # Suhbat tarixini boshqarish (oxirgi 8 ta xabar - tezlik va aniqlik uchun)
    if user_id not in _user_histories:
        _user_histories[user_id] = []

    history = _user_histories[user_id]
    history.append({"role": "user", "content": message_text})
    if len(history) > 8:
        history = history[-6:]
        _user_histories[user_id] = history

    # 1. OpenAI orqali tezkor suhbat (temperature=0.3 aniq faktlar uchun)
    if _openai_client:
        try:
            messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}] + history
            resp = _openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=750
            )
            bot_reply = resp.choices[0].message.content.strip()
            history.append({"role": "assistant", "content": bot_reply})
            return bot_reply
        except Exception as e:
            logger.warning(f"OpenAI chat xatosi: {e}. Gemini sinab ko'riladi...")

    # 2. Gemini fallback
    if _gemini_available:
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(
                model_name="gemini-3.6-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            resp = model.generate_content(message_text)
            bot_reply = resp.text.strip()
            history.append({"role": "assistant", "content": bot_reply})
            return bot_reply
        except Exception as e:
            logger.error(f"Gemini chat xatosi: {e}")
            return f"Kechirasiz, xatolik yuz berdi: {e}"

    return "AI xizmati hozirda mavjud emas."


async def chat_with_ai(user_id: int, message_text: str) -> str:
    """Asinxron AI suhbat."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_chat, user_id, message_text)


def _sync_get_global_news() -> str:
    """Dunyodagi eng so'nggi va muhim global yangiliklar dayjesti (aniq faktlar)."""
    if not is_ai_configured():
        return (
            "⚠️ **AI xizmati sozlanmagan.**\n\n"
            "Global yangiliklar sharhini olish uchun API kalit kerak."
        )

    prompt = (
        "Dunyodagi hozirgi eng muhim, aniq va shov-shuvli global yangiliklar sharhini tayyorla.\n"
        "QOIDALAR: Umumiy gaplar bo'lmasin. Faqat ANIQ DAVLATLAR, ANIQ SHAXSLAR, ANIQ RAQAMLAR VA VOQEALAR.\n\n"
        "Tuzilishi:\n"
        "1. 🌍 **Xalqaro Siyosat va Global Vaziyat:** (Eng asosiy geosiyosiy fakt);\n"
        "2. 💡 **Sun'iy Intellekt va Yangi Texnologiyalar:** (Yirik AI modellari, chip sanoati va ilmiy yutuqlar);\n"
        "3. 📈 **Iqtisodiyot va Bozorlar:** (Neft, dollar kursi, foiz stavkalari va global savdo);\n"
        "4. 🎓 **Xalqaro Ta'lim va Jamiyat:** (Talabalar va dunyo yoshlari hayotidagi muhim o'zgarishlar).\n\n"
        "Har bir punkt 2 tadan lo'nda, aniq faktli gap bo'lsin."
    )
    try:
        return _generate_fast_facts(prompt, max_tokens=650)
    except Exception as e:
        logger.error(f"Yangiliklar olishda xatolik: {e}")
        return f"Yangiliklarni olishda xatolik yuz berdi: {e}"


async def get_global_news() -> str:
    """Asinxron global yangiliklar."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_get_global_news)


def get_spanish_dossier(category: str) -> str:
    """
    Tugmalar bosilganda darhol (0.01 soniyada) boy va aniq faktik dosyelarni qaytarish.
    """
    return FACT_DOSSIERS.get(category, FACT_DOSSIERS['culture'])


def _sync_refresh_spanish_facts() -> str:
    """
    Foydalanuvchi 'Yangi ma'lumot' tugmasini bosganda AI orqali yangi faktlar generatsiya qilish.
    """
    prompt = (
        "Ispaniya, uning boy madaniyati, yashash tarzi yoki ispan tilini tez o'rganish bo'yicha "
        "kutilmagan, kam ma'lum bo'lgan va hayratlanarli 4 TA ANIQ FAKT ber.\n"
        "Har bir faktda aniq raqamlar, ispancha iboralar yoki real hayotiy voqealar bo'lsin. "
        "Umumiy gaplar bo'lmasin."
    )
    return _generate_fast_facts(prompt, max_tokens=650)


async def refresh_spanish_facts() -> str:
    """Asinxron yangi ispancha faktlar generatsiyasi."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_refresh_spanish_facts)
