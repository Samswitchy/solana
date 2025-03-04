import aiosqlite
import asyncio  # Ensure asyncio is imported

async def create_tables():
    async with aiosqlite.connect("graduating.db") as db:  # ✅ Use the same DB file    
        await db.execute("""
            CREATE TABLE IF NOT EXISTS graduating_tokens (
                token_address TEXT PRIMARY KEY,
                twitter_link TEXT,
                risk_score TEXT DEFAULT 'Unknown',
                marketCap REAL,
                liquidity REAL DEFAULT 0,   
                holders INTEGER DEFAULT 0,
                volume REAL DEFAULT 0,
                degen REAL DEFAULT 0,
                pot_token TEXT DEFAULT NULL,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    await db.commit()

# Run the function to create the table
asyncio.run(create_tables())
