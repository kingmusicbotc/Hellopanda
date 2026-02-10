import os

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")

    DATABASE_URL = os.getenv("DATABASE_URL")

    OWNER_NAME = "King G"
    BOT_NAME = "Hello Panda 🐼"
