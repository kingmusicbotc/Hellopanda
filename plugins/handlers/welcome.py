from pyrogram import Client, filters
from pyrogram.types import Message
from core.database import db
from plugins.utils.thumbnail import generate_welcome_image
import random
import traceback

LOG_USER_ID = 8186068163  # <-- your user ID

WELCOME_LINES = [
    "Take your time, explore the space, and jump in whenever you’re ready 🌱",
    "This is a friendly corner of the internet — make yourself comfortable 🐾",
    "Every great conversation starts with a hello. Yours just did ✨",
    "Feel free to listen first or speak up — both are welcome here 💬",
    "You’re among curious minds now. Enjoy the journey 🚀"
]

SIGN_OFFS = [
    "— Hello Panda 🐼",
    "— The Community Team 💜",
    "— Your new digital home 🏡",
    "— Welcome aboard ✨"
]


async def send_welcome(client: Client, message: Message, user):
    try:
        # ── Save user
        await db.execute(
            """
            INSERT INTO users (user_id, username)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
            """,
            user.id,
            user.username
        )

        # ── Generate welcome image
        image = await generate_welcome_image(client, user)

        caption = (
            f"🐼 **Welcome, {user.first_name or 'there'}!**\n\n"
            f"{random.choice(WELCOME_LINES)}\n\n"
            f"🔹 Be respectful\n"
            f"🔹 Share thoughtfully\n"
            f"🔹 Appreciate good vibes\n\n"
            f"{random.choice(SIGN_OFFS)}"
        )

        await message.reply_photo(
            photo=image,
            caption=caption
        )

    except Exception as e:
        # ── Send full error to you
        err_text = (
            "🐼 **Welcome Handler Error**\n\n"
            f"👤 User: {user.id}\n"
            f"🏘 Chat: {message.chat.id}\n\n"
            f"```{traceback.format_exc()}```"
        )

        try:
            await client.send_message(LOG_USER_ID, err_text)
        except Exception:
            pass  # never crash the bot


# ─────────────────────────────────────────
# MAIN HANDLER (MULTI-USER SAFE)
# ─────────────────────────────────────────
@Client.on_message(filters.group & filters.new_chat_members)
async def welcome_handler(client: Client, message: Message):
    for user in message.new_chat_members:
        # Skip bots (including itself)
        if user.is_bot:
            continue

        await send_welcome(client, message, user)

