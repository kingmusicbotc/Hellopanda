from pyrogram import Client, filters
from pyrogram.types import Message
from core.database import db
from plugins.utils.thumbnail import generate_welcome_image
import random
import traceback

ADMIN_ID = 8186068163  # error log receiver

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


async def report_error(client: Client, error: Exception, context: str):
    tb = traceback.format_exc(limit=6)
    text = (
        "🚨 **Welcome Handler Error**\n\n"
        f"📍 **Context:** {context}\n"
        f"❌ **Error:** `{error}`\n\n"
        f"```{tb}```"
    )
    try:
        await client.send_message(ADMIN_ID, text)
    except Exception:
        pass  # never crash on logging


async def send_welcome(client: Client, message: Message, user):
    try:
        # Save user
        await db.execute(
            """
            INSERT INTO users (user_id, username)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
            """,
            user.id,
            user.username
        )

        caption = (
            f"🐼 **Welcome, {user.first_name}!**\n\n"
            f"{random.choice(WELCOME_LINES)}\n\n"
            f"🔹 Be respectful\n"
            f"🔹 Share thoughtfully\n"
            f"🔹 Appreciate good vibes\n\n"
            f"{random.choice(SIGN_OFFS)}"
        )

        # Try image welcome
        try:
            image = await generate_welcome_image(client, user)
            await message.reply_photo(photo=image, caption=caption)
        except Exception as img_error:
            # Fallback to text-only welcome
            await message.reply_text(caption)
            raise img_error

    except Exception as e:
        await report_error(
            client,
            e,
            f"Chat: {message.chat.id} | User: {user.id}"
        )


# ─────────────────────────────────────────
# REAL WELCOME HANDLER
# ─────────────────────────────────────────
@Client.on_message(filters.new_chat_members)
async def welcome_handler(client: Client, message: Message):
    for user in message.new_chat_members:
        await send_welcome(client, message, user)

