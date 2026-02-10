from pyrogram import Client, filters
from pyrogram.types import Message
from core.database import db
from plugins.utils.thumbnail import generate_welcome_image
import random

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
    # Save user to DB
    await db.execute(
        """
        INSERT INTO users (user_id, username)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO NOTHING
        """,
        user.id,
        user.username
    )

    # Generate image (ASYNC, REAL PFP)
    image = await generate_welcome_image(client, user)

    caption = (
        f"🐼 **Welcome, {user.first_name}!**\n\n"
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


# ─────────────────────────────────────────
# Real welcome (new member joins)
# ─────────────────────────────────────────
@Client.on_message(filters.new_chat_members)
async def welcome_handler(client: Client, message: Message):
    user = message.new_chat_members[0]
    await send_welcome(client, message, user)



