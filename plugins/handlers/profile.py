from pyrogram import Client, filters
from pyrogram.types import Message
from core.database import db
from datetime import datetime

@Client.on_message(filters.command("profile"))
async def profile_handler(_, message: Message):
    user = message.from_user
    uid = user.id

    positive = await db.fetchval(
        "SELECT COUNT(*) FROM reputation WHERE receiver=$1 AND value=1",
        uid
    )
    negative = await db.fetchval(
        "SELECT COUNT(*) FROM reputation WHERE receiver=$1 AND value=-1",
        uid
    )

    score = positive - negative

    # Soft, non-judgmental vibe system
    if score >= 15:
        vibe = "🌸 Radiant presence"
    elif score >= 7:
        vibe = "✨ Positive energy"
    elif score >= 0:
        vibe = "🌱 Growing presence"
    else:
        vibe = "🌙 Reflective phase"

    # Optional join date (safe if column exists)
    joined = await db.fetchval(
        "SELECT joined_at FROM users WHERE user_id=$1",
        uid
    )

    joined_text = (
        joined.strftime("%d %b %Y")
        if joined else
        "Unknown"
    )

    await message.reply(
        f"🐼 **Profile Card**\n\n"
        f"👤 {user.mention}\n\n"
        f"➕ **Positive:** {positive}\n"
        f"➖ **Negative:** {negative}\n"
        f"💫 **Score:** {score}\n\n"
        f"🧭 **Vibe:** {vibe}\n"
        f"🕰 **Joined:** {joined_text}\n\n"
        f"✨ Keep being yourself"
    )
