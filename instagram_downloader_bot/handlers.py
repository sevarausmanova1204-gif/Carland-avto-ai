import re
import logging
import uuid

from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatAction
from aiogram.types import FSInputFile, CallbackQuery

from downloader import download_instagram_video, cleanup_file
from config import MAX_FILE_SIZE_MB
from keyboards import (
    get_main_keyboard,
    get_spanish_menu_keyboard,
    get_video_analysis_keyboard
)
from ai_service import (
    analyze_video,
    chat_with_ai,
    get_global_news,
    get_spanish_dossier,
    refresh_spanish_facts,
    save_video_to_cache,
    get_cached_video
)

logger = logging.getLogger(__name__)
router = Router()

# Instagram havolalarini aniqlash uchun mukammal regex
INSTAGRAM_URL_REGEX = re.compile(
    r'https?://(?:www\.)?(?:instagram\.com|instagr\.am)/(?:p|reel|reels|tv|share)(?:/[a-zA-Z0-9_\-]+)+/?(?:\?[^\s]+)?'
)


async def send_smart_message(message: types.Message, text: str, reply_markup=None):
    """
    Uzun xabarlarni Telegram limiti (4096 belgi) bo'yicha bo'lib xavfsiz yuborish.
    """
    if len(text) <= 4000:
        try:
            return await message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)
        except Exception:
            return await message.answer(text, reply_markup=reply_markup)

    # 4000 belgidan uzun bo'lsa bo'laklab yuborish
    parts = [text[i:i + 4000] for i in range(0, len(text), 4000)]
    last_msg = None
    for i, part in enumerate(parts):
        rm = reply_markup if i == len(parts) - 1 else None
        try:
            last_msg = await message.answer(part, parse_mode="Markdown", reply_markup=rm)
        except Exception:
            last_msg = await message.answer(part, reply_markup=rm)
    return last_msg


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    /start komandasi: asosiy menyu va imkoniyatlar.
    """
    welcome_text = (
        "👋 **Assalomu alaykum! N28 AI & Instagram Downloader botiga xush kelibsiz!**\n\n"
        "Men sizga quyidagi sohalarda xizmat qilaman:\n\n"
        "📥 **1. Instagram Video & Reels:**\n"
        "• Asl va eng yuqori sifatda (Full HD/4K) videolarni yuklab beraman.\n\n"
        "🤖 **2. Sun'iy Intellekt (AI) Tahlil:**\n"
        "• Yuklangan har qanday videoni mazmuni, asosiy g'oyalari va tarjimasini tahlil qilib beraman.\n\n"
        "💬 **3. AI Suhbatdosh:**\n"
        "• Menga istalgan savolingizni yozing, birgalikda fikrlashamiz va suhbatlashamiz.\n\n"
        "🌍 **4. Dunyo Yangiliklari:**\n"
        "• Global siyosat, texnologiya va jamiyatdagi eng dolzarb voqealar dayjesti.\n\n"
        "🇪🇸 **5. Ispan Tili & Xalqaro Imkoniyatlar:**\n"
        "• Ispan tili darslari, grantlar (Erasmus, Fundación Carolina) va xalqaro masofaviy vakansiyalar.\n\n"
        "👇 _Quyidagi menyulardan birini tanlang yoki Instagram havolasini yuboring!_"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Qo'llanma")
async def cmd_help(message: types.Message):
    """
    Qo'llanma va botdan foydalanish yo'riqnomasi.
    """
    help_text = (
        "ℹ️ **Botdan foydalanish bo'yicha qo'llanma:**\n\n"
        "🔹 **Video yuklash:** Instagram havolasini (masalan: `https://www.instagram.com/reel/...`) shunchaki botga yuboring.\n"
        "🔹 **Videoni tahlil qilish:** Video yuklangach, uning ostidagi **[🤖 Videoni AI bilan tahlil qilish]** tugmasini bosing.\n"
        "🔹 **AI bilan suhbat:** Istalgan matnli savol yuborsangiz, AI suhbatdoshingiz sizga javob qaytaradi.\n"
        "🔹 **Global yangiliklar:** Menyudagi **'🌍 Global Yangiliklar'** tugmasini bosing.\n"
        "🔹 **Ispan tili & Ishlar:** Menyudagi **'🇪🇸 Ispan tili & Ishlar'** bo'limi orqali darslar, grantlar va vakansiyalarni ko'ring.\n\n"
        f"⚠️ Telegram limiti: Maksimal video hajmi {MAX_FILE_SIZE_MB}MB."
    )
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_main_keyboard())


# ==========================================
# 🌍 GLOBAL YANGILIKLAR
# ==========================================
@router.message(F.text == "🌍 Global Yangiliklar")
async def handle_global_news(message: types.Message):
    """Dunyodagi dolzarb yangiliklar dayjesti."""
    status = await message.answer("⏳ **Dunyo yangiliklari tahlil qilinmoqda...**", parse_mode="Markdown")
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    news_text = await get_global_news()
    try:
        await status.delete()
    except Exception:
        pass

    await send_smart_message(message, news_text, reply_markup=get_main_keyboard())


# ==========================================
# 🇪🇸 ISPAN TILI VA VAKANSIYALAR BO'LIMI
# ==========================================
@router.message(F.text == "🇪🇸 Ispan tili & Ishlar")
async def handle_spanish_menu(message: types.Message):
    """Ispan tili, madaniyat, hayot tarzi va vakansiyalar bosh menyusi."""
    intro_text = (
        "🇪🇸 **Ispaniya Madaniyati, Yashash Tarzi & Til Markazi**\n\n"
        "Ispaniya haqida nimalarni bilishni istaysiz?\n\n"
        "• 💃 **Urf-odatlar & Udumlar:** Siesta, Sobremesa, qiziqarli bayramlar va etiket;\n"
        "• 🏖 **Yashash tarzi & Hayot:** Ispanlarning kun tartibi, xarajatlar va qiziqishlari;\n"
        "• ⚡️ **Tilni tez o'rganish sirlari:** A1 dan B2 gacha 2-3 barobar tezroq chiqish yo'llari;\n"
        "• 📚 **Kundalik jonli iboralar:** Har kuni ishlatiladigan so'zlar va sleng;\n"
        "• 💼 **Ish, Grantlar & Ta'lim:** Erasmus, stipendiyalar va xalqaro masofaviy vakansiyalar.\n\n"
        "👇 _Quyidagi tugmalardan birini tanlang:_"
    )
    await message.answer(intro_text, parse_mode="Markdown", reply_markup=get_spanish_menu_keyboard())


@router.callback_query(F.data.startswith("es_"))
async def handle_spanish_callback(callback: CallbackQuery):
    """Ispan tili va madaniyati bo'yicha tezkor va faktlarga boy ma'lumotlar."""
    if callback.data == "es_refresh":
        await callback.answer("⏳ Yangi faktlar tayyorlanmoqda...")
        await callback.bot.send_chat_action(chat_id=callback.message.chat.id, action=ChatAction.TYPING)
        info_text = await refresh_spanish_facts()
    else:
        category_map = {
            "es_culture": "culture",
            "es_lifestyle": "lifestyle",
            "es_speed_learning": "speed_learning",
            "es_learning": "learning",
            "es_jobs_grants": "jobs_grants",
            "es_resources": "resources",
        }
        category = category_map.get(callback.data, "culture")
        info_text = get_spanish_dossier(category)
        await callback.answer("✅ Tayyor!")

    try:
        await callback.message.edit_text(
            info_text,
            parse_mode="Markdown",
            reply_markup=get_spanish_menu_keyboard()
        )
    except Exception:
        await callback.message.answer(
            info_text,
            parse_mode="Markdown",
            reply_markup=get_spanish_menu_keyboard()
        )


# ==========================================
# 💬 AI SUHBAT REJIMI
# ==========================================
@router.message(F.text == "💬 AI Suhbat")
async def handle_ai_chat_intro(message: types.Message):
    """AI suhbat rejimiga taklif."""
    intro = (
        "💬 **AI Suhbatdosh rejimiga xush kelibsiz!**\n\n"
        "Men bilan istalgan mavzuda suhbatlashishingiz mumkin:\n"
        "• Dunyodagi tendensiyalar va xalqaro siyosat;\n"
        "• Ispan va ingliz tillari bo'yicha savollar (tarjima, qoidalar, so'zlar);\n"
        "• Xalqaro grantlar va chet elda o'qish;\n"
        "• Masofaviy ishlar va karyera maslahatlari.\n\n"
        "✍️ _Savolingiz yoki fikringizni yozib yuboring:_"
    )
    await message.answer(intro, parse_mode="Markdown")


# ==========================================
# 📥 INSTAGRAM VIDEO VA AI TAHLIL
# ==========================================
@router.message(F.text.regexp(INSTAGRAM_URL_REGEX))
async def handle_instagram_link(message: types.Message):
    """Instagram havolasini qabul qilish va AI tahlil tugmasi bilan yuborish."""
    match = INSTAGRAM_URL_REGEX.search(message.text)
    if not match:
        await message.answer("⚠️ Instagram havolasi noto'g'ri formatda.")
        return

    url = match.group(0)
    status_msg = await message.answer("⏳ **Video asl sifatda yuklab olinmoqda...**\nIltimos, kuting.", parse_mode="Markdown")
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)

    file_path = None
    cache_id = uuid.uuid4().hex[:10]

    try:
        download_result = await download_instagram_video(url)
        file_path = download_result.get('file_path')

        if download_result.get('is_too_large'):
            direct_url = download_result.get('direct_url')
            text = (
                f"⚠️ **Video hajmi {MAX_FILE_SIZE_MB}MB dan katta!**\n"
                "Telegram cheklovi tufayli bot orqali yuborib bo'lmaydi.\n\n"
            )
            if direct_url:
                text += f"[Ushbu havola orqali brauzerda yuklab olishingiz mumkin]({direct_url})"
            await status_msg.edit_text(text, parse_mode="Markdown")
            return

        # Sarlavha tayyorlash
        caption = download_result.get('title') or ""
        if len(caption) > 750:
            caption = caption[:750] + "..."

        owner = download_result.get('owner')
        bot_info = await message.bot.get_me()
        bot_username = f"@{bot_info.username}" if bot_info.username else "bot"

        footer = ""
        if owner:
            footer += f"\n\n👤 Muallif: @{owner}"
        footer += f"\n✨ {bot_username} orqali asl sifatda yuklandi"
        caption += footer

        # Videoni keshda saqlaymiz (agar foydalanuvchi AI tahlil tugmasini bossa)
        save_video_to_cache(cache_id, {
            'file_path': file_path,
            'caption': download_result.get('title') or "",
            'owner': owner,
            'direct_url': download_result.get('direct_url')
        })

        video_input = FSInputFile(file_path)

        await message.answer_video(
            video=video_input,
            caption=caption,
            duration=download_result.get('duration'),
            width=download_result.get('width'),
            height=download_result.get('height'),
            supports_streaming=True,
            reply_markup=get_video_analysis_keyboard(cache_id)
        )

        try:
            await status_msg.delete()
        except Exception:
            pass

    except PermissionError:
        user_error = "❌ **Xatolik:** Ushbu Instagram akkaunt yopiq (private). Faqat ochiq profillardagi videolarni yuklash mumkin."
        try:
            await status_msg.edit_text(user_error, parse_mode="Markdown")
        except Exception:
            await message.answer(user_error, parse_mode="Markdown")
        if file_path:
            cleanup_file(file_path)

    except FileNotFoundError:
        user_error = "❌ **Xatolik:** Video topilmadi yoki o'chirilgan."
        try:
            await status_msg.edit_text(user_error, parse_mode="Markdown")
        except Exception:
            await message.answer(user_error, parse_mode="Markdown")
        if file_path:
            cleanup_file(file_path)

    except ValueError as ve:
        user_error = f"⚠️ {str(ve)}"
        try:
            await status_msg.edit_text(user_error, parse_mode="Markdown")
        except Exception:
            await message.answer(user_error, parse_mode="Markdown")
        if file_path:
            cleanup_file(file_path)

    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}", exc_info=True)
        user_error = (
            "❌ **Videoni yuklab bo'lmadi.**\n"
            "Havola to'g'riligini tekshiring yoki birozdan so'ng qayta urinib ko'ring."
        )
        try:
            await status_msg.edit_text(user_error, parse_mode="Markdown")
        except Exception:
            await message.answer(user_error, parse_mode="Markdown")
        if file_path:
            cleanup_file(file_path)


# ==========================================
# 🤖 AI VIDEO TAHLIL CALLBACK
# ==========================================
@router.callback_query(F.data.startswith("ai_analyze:"))
async def handle_ai_video_analysis(callback: CallbackQuery):
    """Yuklangan videoni AI bilan tahlil qilish."""
    cache_id = callback.data.split(":", 1)[1]
    cached_data = get_cached_video(cache_id)

    if not cached_data:
        await callback.answer("⚠️ Videoning tahlil qilish muddati tugagan.", show_alert=True)
        return

    await callback.answer("🤖 Video AI tomonidan tahlil qilinmoqda...")
    status = await callback.message.reply("🧠 **Videoni ko'rib chiqyapman va tahlil tayyorlayapman...**", parse_mode="Markdown")
    await callback.bot.send_chat_action(chat_id=callback.message.chat.id, action=ChatAction.TYPING)

    file_path = cached_data.get('file_path')
    caption = cached_data.get('caption', '')
    owner = cached_data.get('owner')

    analysis_result = await analyze_video(file_path, caption, owner)

    try:
        await status.delete()
    except Exception:
        pass

    # Tahlil natijasini yuborish
    header = "📊 **VIDEO TAHLILI (AI Natijasi):**\n\n"
    await send_smart_message(callback.message, header + analysis_result)

    # Tahlil qilib bo'lingach, agar video fayli mavjud bo'lsa xotirani tozalaymiz
    if file_path:
        cleanup_file(file_path)


# ==========================================
# 💬 ERKIN SUHBAT VA MATNLAR
# ==========================================
@router.message(F.text)
async def handle_general_chat(message: types.Message):
    """
    Foydalanuvchining barcha erkin savollari va xabarlariga AI orqali javob berish.
    """
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    ai_response = await chat_with_ai(message.from_user.id, message.text)
    await send_smart_message(message, ai_response)
