import asyncio
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

import requests
import instaloader
from instaloader.exceptions import (
    LoginRequiredException,
    ProfileNotExistsException,
    QueryReturnedNotFoundException,
)
import yt_dlp

from config import DOWNLOADS_DIR, MAX_FILE_SIZE_BYTES

# Instaloader instansiyasi (faqat kerakli video ma'lumotlarini olish uchun yengillashtirilgan)
_loader = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
    quiet=True
)

# Global persistent session tezkor yuklash uchun (TCP handshake qayta qilinmaydi)
_http_session = requests.Session()
_http_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
})


def extract_shortcode(url: str) -> Optional[str]:
    """
    Instagram havolasidan post yoki reel shortcode'ni ajratib olish.
    """
    # 1. To'g'ridan-to'g'ri regex orqali qidirish
    match = re.search(r'/(?:reel|reels|p|tv|share/reel|share/p)/([a-zA-Z0-9_\-]+)', url)
    if match:
        return match.group(1)

    # 2. Agar qisqartirilgan havola bo'lsa, redirect orqali tekshirish
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        match = re.search(r'/(?:reel|reels|p|tv|share/reel|share/p)/([a-zA-Z0-9_\-]+)', resp.url)
        if match:
            return match.group(1)
    except Exception:
        pass

    return None


def _download_via_instaloader(shortcode: str, output_path: Path) -> Dict[str, Any]:
    """
    Instaloader orqali to'g'ridan-to'g'ri Instagram CDN manzilidan asl sifatdagi videoni yuklab olish.
    Hech qanday cookie yoki login talab qilinmaydi!
    """
    try:
        post = instaloader.Post.from_shortcode(_loader.context, shortcode)
    except (LoginRequiredException,):
        raise PermissionError("Ushbu Instagram akkaunt yopiq (private). Faqat ochiq profillardagi videolarni yuklash mumkin.")
    except (ProfileNotExistsException, QueryReturnedNotFoundException):
        raise FileNotFoundError("Video topilmadi yoki o'chirilgan.")
    except Exception as e:
        raise RuntimeError(f"Instaloader xatosi: {e}")

    video_url = None
    if post.is_video and post.video_url:
        video_url = post.video_url
    elif post.typename == 'GraphSidecar':
        # Karuseldagi videoni qidiramiz
        for node in post.get_sidecar_nodes():
            if node.is_video and node.video_url:
                video_url = node.video_url
                break

    if not video_url:
        raise ValueError("Ushbu postda video topilmadi (bu faqat rasm yoki matn bo'lishi mumkin).")

    # Videoni 512KB li bloklarda tezkor yuklab olamiz
    with _http_session.get(video_url, stream=True, timeout=25) as r:
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:
                    f.write(chunk)

    file_size = output_path.stat().st_size

    caption = post.caption or "Instagram Video"
    duration = int(post.video_duration) if post.video_duration else None

    return {
        'file_path': str(output_path),
        'title': caption,
        'duration': duration,
        'width': None,
        'height': None,
        'file_size': file_size,
        'is_too_large': file_size > MAX_FILE_SIZE_BYTES,
        'direct_url': video_url,
        'owner': post.owner_username,
    }


def _download_via_ytdlp(url: str, output_template: str) -> Dict[str, Any]:
    """
    yt-dlp orqali zaxira yuklash usuli.
    """
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if not info:
            raise ValueError("Video ma'lumotlarini olib bo'lmadi.")

        if 'entries' in info and info['entries']:
            info = info['entries'][0]

        downloaded_file = Path(ydl.prepare_filename(info))
        if not downloaded_file.exists():
            matches = list(downloaded_file.parent.glob(f"{downloaded_file.stem}.*"))
            if matches:
                downloaded_file = matches[0]
            else:
                raise FileNotFoundError("Yuklab olingan video fayli topilmadi.")

        file_size = downloaded_file.stat().st_size

        return {
            'file_path': str(downloaded_file),
            'title': info.get('title') or info.get('description') or "Instagram Video",
            'duration': info.get('duration'),
            'width': info.get('width'),
            'height': info.get('height'),
            'file_size': file_size,
            'is_too_large': file_size > MAX_FILE_SIZE_BYTES,
            'direct_url': info.get('url'),
            'owner': info.get('uploader'),
        }


def _sync_download(url: str) -> Dict[str, Any]:
    """
    Multi-engine yuklash mexanizmi:
    1-navbatda to'g'ridan-to'g'ri Instaloader (CDN stream)
    Agar zarur bo'lsa, 2-navbatda yt-dlp
    """
    unique_id = uuid.uuid4().hex[:10]
    shortcode = extract_shortcode(url)

    # 1. Instaloader usulini sinab ko'rish
    if shortcode:
        try:
            output_file = DOWNLOADS_DIR / f"ig_{unique_id}.mp4"
            return _download_via_instaloader(shortcode, output_file)
        except PermissionError:
            # Agar haqiqatan yopiq profil bo'lsa
            raise
        except Exception as e:
            logging.warning(f"Instaloader orqali yuklashda xatolik: {e}. yt-dlp ga o'tilmoqda...")

    # 2. yt-dlp zaxira usuli
    output_template = str(DOWNLOADS_DIR / f"ig_{unique_id}.%(ext)s")
    return _download_via_ytdlp(url, output_template)


async def download_instagram_video(url: str) -> Dict[str, Any]:
    """
    Asinxron yuklab olish funksiyasi (thread'da chaqiriladi).
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_download, url)


def cleanup_file(filepath: Optional[str]) -> None:
    """
    Vaqtinchalik yuklangan faylni serverdan o'chirish.
    """
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass
