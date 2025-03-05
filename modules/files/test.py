import aiosqlite
import asyncio
import logging

# ✅ Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_graduating_table():
    async with aiosqlite.connect("graduating.db") as conn:
        cursor = await conn.execute("PRAGMA table_info(graduating_tokens)")
        columns = await cursor.fetchall()
        
        if not columns:
            logger.warning("⚠️ Table 'graduating_tokens' does NOT exist or has no columns!")
        else:
            logger.info(f"🔍 Columns in graduating_tokens: {columns}")
            print("Columns:", columns)  # ✅ Explicitly print to terminal

# ✅ Run the async function
asyncio.run(check_graduating_table())
