from pyrogram import Client, filters
from pyrogram.types import Message
import random

REACTION_EMOJIS = [
    "🐼", "🌸", "✨", "💜", "🌿", "🫶",
    "😊", "🤍", "🐾", "🌙", "☁️"
]

REACTION_CHANCE = 0.15  # 15%

@Client.on_message(
    filters.group
    & ~filters.service
    & ~filters.regex(r"^/")  # ← ignore commands safely
)
async def random_react_handler(client: Client, message: Message):
    # Ignore bots
    if message.from_user and message.from_user.is_bot:
        return

    # Only text messages
    if not message.text:
        return

    # Probability gate
    if random.random() > REACTION_CHANCE:
        return

    try:
        await client.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=random.choice(REACTION_EMOJIS)
        )
    except Exception:
        pass
