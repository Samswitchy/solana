import aiosqlite

async def check_tables():
    async with aiosqlite.connect("your_database.db") as db:
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table';") as cursor:
            tables = await cursor.fetchall()
            print("Existing tables:", tables)

import asyncio
asyncio.run(check_tables())
