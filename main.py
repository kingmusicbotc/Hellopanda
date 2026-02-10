import threading
from pyrogram import Client, idle
from config import Config
from core.database import connect_db, close_db
from core.logger import setup_logger
from app import app as web_app

logger = setup_logger("HelloPanda")

bot = Client(
    "hello-panda",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    workers=50,
    plugins=dict(root="plugins")
)

def run_web():
    web_app.run(host="0.0.0.0", port=8000)

async def main():
    logger.info("🐼 Hello Panda starting...")
    await connect_db()

    threading.Thread(target=run_web, daemon=True).start()
    logger.info("🌐 Web dashboard started")

    await bot.start()
    logger.info("✅ Bot is live")
    await idle()

    logger.info("🌙 Bot stopping...")
    await bot.stop()
    await close_db()

bot.run(main())
