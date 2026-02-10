from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from core.database import db

LOG_CHAT_ID = -1003527724170


# ─────────────────────────────────────────
# PRIVATE /start
# ─────────────────────────────────────────
@Client.on_message(filters.command("start"))
async def start_private(client: Client, message: Message):
    user = message.from_user

    # Check if user exists
    exists = await db.fetchval(
        "SELECT 1 FROM users WHERE user_id = $1",
        user.id
    )

    if not exists:
        await db.execute(
            "INSERT INTO users (user_id, username) VALUES ($1, $2)",
            user.id,
            user.username
        )

        total_users = await db.fetchval("SELECT COUNT(*) FROM users")

        await client.send_message(
            LOG_CHAT_ID,
            (
                "🐼 **New User Started the Bot**\n\n"
                f"👤 **Name:** {user.first_name}\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"🔗 **Username:** @{user.username or 'None'}\n\n"
                f"📊 **Total Users:** {total_users}"
            )
        )

    caption = (
        "🐼 **Hello Panda**\n\n"
        "A calm, welcoming space designed for\n"
        "meaningful conversations and good energy.\n\n"
        "🌸 Gentle vibes\n"
        "💬 Thoughtful chats\n"
        "💜 Community first\n\n"
        "Feel free to explore at your own pace.\n"
        "I’ll be right here whenever you need me ✨"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ Add to Group",
                    url=f"https://t.me/{client.me.username}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton("🛠 Support", url="https://t.me/+99pZe7mYOOQxYTQx"),
                InlineKeyboardButton("🌐 Web", url="https://hellopanda.onrender.com/")
            ]
        ]
    )

    await message.reply_photo(
        photo="Assets/start.jpeg",
        caption=caption,
        reply_markup=keyboard
    )

