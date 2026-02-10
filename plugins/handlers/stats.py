from pyrogram import Client, filters
from pyrogram.types import Message
from core.database import db


@Client.on_message(filters.command("stats"))
async def stats_handler(_, message: Message):
    users = await db.fetchval("SELECT COUNT(*) FROM users")
    groups = await db.fetchval("SELECT COUNT(*) FROM groups")

    graph = generate_stats_graph(users, groups)

    caption = (
        "🐼 **Hello Panda · Stats**\n\n"
        f"👥 **Total Users:** {users}\n"
        f"🏘️ **Total Groups:** {groups}\n\n"
        "🌱 Growing calmly, one community at a time.\n"
        "✨ Thank you for being part of the journey."
    )

    await message.reply_photo(
        photo=graph,
        caption=caption
    )

import matplotlib.pyplot as plt
import io

def generate_stats_graph(users: int, groups: int):
    labels = ["Users", "Groups"]
    values = [users, groups]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values)
    plt.title("Hello Panda · Community Reach")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=160)
    plt.close()
    img.seek(0)
    img.name = "stats.png"
    return img


from pyrogram import Client, filters
from pyrogram.types import Message
from core.database import db

@Client.on_message(filters.group & filters.service)
async def track_group(_, message: Message):
    if message.new_chat_members:
        for user in message.new_chat_members:
            if user.is_bot:
                await db.execute(
                    """
                    INSERT INTO groups (chat_id, title)
                    VALUES ($1, $2)
                    ON CONFLICT (chat_id) DO NOTHING
                    """,
                    message.chat.id,
                    message.chat.title
                )
