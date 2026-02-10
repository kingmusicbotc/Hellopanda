import asyncpg
from config import Config
from core.logger import setup_logger
from pathlib import Path

logger = setup_logger("DB")
db: asyncpg.Pool | None = None

SCHEMA_PATH = Path("sql/schema.sql")

async def connect_db():
    global db
    db = await asyncpg.create_pool(Config.DATABASE_URL, min_size=1, max_size=5)
    logger.info("📦 PostgreSQL connected")
    await run_migration()

async def run_migration():
    if not SCHEMA_PATH.exists():
        logger.warning("⚠️ schema.sql not found, skipping migration")
        return

    async with db.acquire() as conn:
        schema_sql = SCHEMA_PATH.read_text()
        await conn.execute(schema_sql)
        logger.info("✅ Database schema ensured")

async def close_db():
    if db:
        await db.close()
        logger.info("📦 PostgreSQL closed")
