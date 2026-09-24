"""Foydalanuvchilar faolligini kuzatish (oddiy analitika) qatlami.

Har bir muhim harakat (start, menyu bosish, mashina/mahsulot ko'rish, AI
chat) shu yerda yozib boriladi va admin `/stats` buyrug'i orqali ko'rilishi
mumkin. Ma'lumot `carland.db`dan ATAYLAB alohida faylga (`analytics.db`)
yoziladi va shu bazadagi kabi `PERSIST_DIR`ga joylashadi (bot/config.py'dagi
PERSIST_DIR izohiga qarang) — `carland.db` git-deploy paytida qayta
yozilib turadi, agar statistika o'sha faylga yozilsa, har deployda
yo'qolib ketardi.

Statistika yozish HECH QACHON botning asosiy ishiga (foydalanuvchiga
javob berishiga) to'sqinlik qilmasligi kerak — shu sabab `log_event`
ichidagi har qanday xatolik jim yutiladi.
"""
import sqlite3
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

from .config import PERSIST_DIR

EVENTS_DB_PATH = PERSIST_DIR / "analytics.db"


@contextmanager
def _conn():
    conn = sqlite3.connect(EVENTS_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _ensure_schema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            first_name TEXT,
            lang TEXT,
            event_type TEXT NOT NULL,
            detail TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id)")


def log_event(user, lang: str, event_type: str, detail: str = ""):
    """`user` — `update.effective_user` / `query.from_user` (telegram.User).
    None bo'lsa yoki yozishda xatolik yuz bersa, jim o'tkazib yuboriladi."""
    if user is None:
        return
    try:
        with _conn() as conn:
            _ensure_schema(conn)
            conn.execute(
                "INSERT INTO events (ts, user_id, username, first_name, lang, event_type, detail) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    user.id,
                    user.username or "",
                    user.first_name or "",
                    lang or "",
                    event_type,
                    (detail or "")[:200],
                ),
            )
    except Exception:  # noqa: BLE001
        pass


def build_stats_report(days: int = 7) -> str:
    """Oxirgi `days` kunlik faollik bo'yicha, Telegram xabariga tayyor
    (Markdown) hisobot matnini quradi."""
    since_dt = datetime.now(timezone.utc) - timedelta(days=days)
    since = since_dt.isoformat(timespec="seconds")

    with _conn() as conn:
        _ensure_schema(conn)
        period_rows = [
            dict(r)
            for r in conn.execute(
                "SELECT ts, user_id, lang, event_type, detail FROM events WHERE ts >= ? ORDER BY ts",
                (since,),
            ).fetchall()
        ]
        first_seen = {
            r["user_id"]: r["first_ts"]
            for r in conn.execute(
                "SELECT user_id, MIN(ts) AS first_ts FROM events GROUP BY user_id"
            ).fetchall()
        }

    if not period_rows:
        return f"📊 Oxirgi {days} kunda hech qanday faollik qayd etilmagan."

    unique_users = {r["user_id"] for r in period_rows}
    new_users = {uid for uid in unique_users if first_seen.get(uid, "") >= since}

    daily = Counter(r["ts"][:10] for r in period_rows)

    car_counter = Counter()
    ai_count = 0
    lang_last_seen = {}
    for r in period_rows:
        if r["event_type"] in ("car_view", "oil_price_view") and r["detail"]:
            model = r["detail"].split(":", 1)[-1]
            car_counter[model] += 1
        if r["event_type"] == "ai_chat":
            ai_count += 1
        if r["lang"]:
            lang_last_seen[r["user_id"]] = r["lang"]

    lang_counts = Counter(lang_last_seen.values())
    total_lang_users = sum(lang_counts.values()) or 1

    lines = [
        f"📊 *Carland bot statistikasi* (oxirgi {days} kun)",
        "",
        f"👥 Faol foydalanuvchilar: *{len(unique_users)}*",
        f"🆕 Yangi foydalanuvchilar: *{len(new_users)}*",
        f"📨 Jami harakatlar: *{len(period_rows)}*",
        f"💬 AI chat so'rovlari: *{ai_count}*",
        "",
        "📅 *Kunlar bo'yicha faollik:*",
    ]
    for day in sorted(daily):
        lines.append(f"  {day}: {daily[day]}")

    if car_counter:
        lines.append("")
        lines.append("🚗 *Eng ko'p so'ralgan mashinalar:*")
        for i, (model, cnt) in enumerate(car_counter.most_common(10), 1):
            lines.append(f"  {i}. {model} — {cnt}")

    if lang_counts:
        lines.append("")
        lines.append("🌐 *Til bo'yicha (oxirgi ko'rilgan):*")
        for lang, cnt in lang_counts.most_common():
            pct = round(cnt / total_lang_users * 100)
            lines.append(f"  {lang.upper()}: {cnt} ({pct}%)")

    return "\n".join(lines)
