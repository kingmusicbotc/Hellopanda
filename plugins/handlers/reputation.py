from pyrogram import Client, filters
from pyrogram.types import Message
from core.database import db
import random

RESPONSES_POS = [
    "🐼 {user} just received some appreciation 💜",
    "✨ Good vibes sent to {user}",
    "🌸 Kind energy shared with {user}",
    "🐾 {user} was appreciated",
]

RESPONSES_NEG = [
    "🐼 Feedback noted for {user}",
    "🌙 {user} received some reflection",
    "📝 Thoughtful feedback shared with {user}",
    "🐾 {user} was noted",
]


@Client.on_message(
    filters.group
    & filters.reply
    & filters.regex(r"^[+-]($|\s+)")
)
async def reputation_handler(_, message: Message):
    giver = message.from_user
    receiver = message.reply_to_message.from_user

    if not receiver:
        return

    if giver.id == receiver.id:
        await message.reply("🐼 You can’t rate yourself.")
        return

    value = 1 if message.text.startswith("+") else -1
    reason = message.text[1:].strip() or "No reason provided"

    await db.execute(
        """
        INSERT INTO reputation (giver, receiver, value, reason)
        VALUES ($1, $2, $3, $4)
        """,
        giver.id,
        receiver.id,
        value,
        reason
    )

    mention = receiver.mention

    text = random.choice(
        RESPONSES_POS if value == 1 else RESPONSES_NEG
    ).format(user=mention)

    await message.reply(text)


@Client.on_message(filters.command("karma"))
async def karma_handler(_, message: Message):
    user = (
        message.reply_to_message.from_user
        if message.reply_to_message
        else message.from_user
    )

    positive = await db.fetchval(
        "SELECT COUNT(*) FROM reputation WHERE receiver=$1 AND value=1",
        user.id
    )
    negative = await db.fetchval(
        "SELECT COUNT(*) FROM reputation WHERE receiver=$1 AND value=-1",
        user.id
    )

    score = positive - negative

    vibe = (
        "🌸 Radiant energy"
        if score >= 10 else
        "✨ Good vibes"
        if score >= 3 else
        "🌱 Growing presence"
        if score >= 0 else
        "🌙 Reflective phase"
    )

    await message.reply(
        f"🐼 **Karma Card**\n\n"
        f"👤 {user.first_name}\n\n"
        f"➕ {positive}\n"
        f"➖ {negative}\n\n"
        f"💫 **Score:** {score}\n"
        f"🧭 {vibe}"
    )
