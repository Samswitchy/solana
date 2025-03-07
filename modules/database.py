import sqlite3
import aiosqlite
import asyncio
import datetime
import logging
from modules.config import DATABASE_NAME

from modules.tgalert import send_telegram_alert  # Import the function from tgalert module



logger = logging.getLogger(__name__)


def init_db():
    """Initialize the database and create table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_name TEXT,
            token_address TEXT UNIQUE,
            twitter_link TEXT,
            int_marketCap REAL,
            marketCap REAL,
            ath REAL DEFAULT 0,
            liquidity REAL,
            trade TEXT DEFAULT 'HOLD',
            volume REAL DEFAULT 0, -- ✅ Trading volume
            degen TEXT DEFAULT NULL, -- ✅ degen token flag
            status TEXT DEFAULT 'Active',  -- 'active', 'graduating', 'rugged', etc.
            risk_score TEXT DEFAULT 'Unknown',  -- ✅ Risk Category (Safe, Medium, High)
            pot_token TEXT DEFAULT NULL, -- ✅ Potential token flag
            holders REAL,  -- ✅ New column for holders
            xmade REAL,  -- ✅ New column for number of x made      
            initial_at TEXT DEFAULT CURRENT_TIMESTAMP,  -- ✅ Stores when token was first added
            ath_at TEXT DEFAULT NULL, -- Set when the current all time hits 
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP -- ✅ Store time when marketCap was updated

        )
    """)
    conn.commit()
    conn.close()


async def enable_wal_mode():
    """Enable WAL mode to prevent database locking issues."""
    async with aiosqlite.connect(DATABASE_NAME) as conn:
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.commit()
    logger.info("✅ WAL mode enabled for graduating_tokens database.")

#--------------------------------------------------------

# ✅ Move to Graduating DB
async def move_to_graduating_db(token_address, marketCap, status):
    pot_token = "NO"  # Initialize variable to avoid reference errors
    trade = "NO"
    #if 55000 <= marketCap <= 70000:
    if 55000 <= marketCap <= 70000:
        pot_token = marketCap
        trade = "YES"
        message = f"Token: {token_address}\nMarket Cap: {marketCap}\nPot Token: {pot_token}"
        send_telegram_alert(message)  # Send alert

    async with aiosqlite.connect(DATABASE_NAME) as conn:
        await conn.execute("""
            UPDATE tokens 
            SET marketCap = ?, status = ?, pot_token = ?
            WHERE token_address = ?
        """, (marketCap, status, pot_token, token_address))
        await conn.commit()
    
    logger.info(f"✅ {token_address} updated in tokens.db with Status: {status} MarketCap: {marketCap}")


async def fetch_graduating_tokens():
    """Fetch token addresses, market caps, and ATH from graduating.db asynchronously."""
    async with aiosqlite.connect(DATABASE_NAME) as conn:
        cursor = await conn.execute("SELECT token_address, marketCap, ath FROM tokens")
        tokens = await cursor.fetchall()

    #logger.info(f"📊 Raw Database Output: {tokens}")  # ✅ Log raw data

    # ✅ Ensure 'marketCap' and 'ath' are never None
    formatted_tokens = [
        (row[0], row[1] if row[1] is not None else 0, row[2] if row[2] is not None else 0)
        for row in tokens
    ]

  #  logger.info(f"📊 Processed Tokens: {formatted_tokens}")  # ✅ Log cleaned data
    return formatted_tokens



async def batch_update_tokens(updates):
    """Batch update market cap, volume, pot_token, and other fields for graduating tokens."""
    

    if not updates:
        return  # No updates to process

    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            await conn.executemany("""
                UPDATE tokens
                SET marketCap = ?, volume = ?, pot_token = ?, liquidity = ?, trade = ?, degen = ?, ath = ?, ath_at = ?
                WHERE token_address = ?
            """, updates)
            await conn.commit()
        
        logger.info(f"✅ Batch update successful for {len(updates)} tokens")
    except Exception as e:
        logger.error(f"❌ Batch update error: {e}")

#-----------------------------------------------------

async def inactive_to_db(token_address, status):
    #pot_token = "NO"  # Initialize variable to avoid reference errors
    
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            await conn.execute("""
                UPDATE tokens
                SET status = ?
                WHERE token_address = ?
            """, (status,  token_address))
            await conn.commit()

        logger.info(f"✅ {token_address} updated: MarketCap: {status}")
    except Exception as e:
        logger.error(f"❌ Error updating {token_address}: {e} in inactive")


#----------------------------------------------------

async def delete_graduating_token(token_address):
     #Delete a token from the graduating status in tokens.db.
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            await conn.execute("DELETE FROM tokens WHERE token_address = ?", (token_address,))
            await conn.commit()
        
        logger.info(f"🗑️ Deleted {token_address} from tokens.db")
    except Exception as e:
        logger.error(f"❌ Error deleting token {token_address}: {e}")
        """
"""
#----------------------------------------------------
#Below is the updated code for the file database_name

async def get_previous_marketCap(token_address):
    """Fetch the last stored market cap from the database asynchronously."""
    async with aiosqlite.connect(DATABASE_NAME) as conn:
        async with conn.execute("SELECT int_marketCap FROM tokens WHERE token_address = ?", (token_address,)) as cursor:
            result = await cursor.fetchone()

    return result[0] if result else None

async def save_to_db(token_name, token_address, twitter_link, int_marketCap, marketCap):
    """Asynchronously save token data to database."""
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            cursor = await conn.cursor()
            await cursor.execute("""
                INSERT OR IGNORE INTO tokens (token_name, token_address, twitter_link, int_marketCap, marketCap, ath) 
                VALUES (?, ?, ?, ?, ?)
            """, (token_name, token_address, twitter_link, int_marketCap, marketCap, ath))
            await conn.commit()  # ✅ Use `await` for async commit

        logger.info(f"✅ Saved to DB: {token_name} - {token_address} - Market Cap: {int_marketCap} - Market: {marketCap}")
    except Exception as e:
        logger.error(f"❌ Database Error in save to db: {e}")

async def calculate_risk(marketCap, volume):
    """Calculate risk score based on market cap and volume."""
    try:
        marketCap, volume = float(marketCap), float(volume)
        if marketCap >= 50000 and volume >= 10000:
            return "High Risk"
        elif marketCap >= 30000:
            return "Medium Risk"
        return "Low Risk"
    except ValueError:
        return "Invalid Data"

# ✅ Update Market Data
async def market_to_db(token_address, marketCap, volume, liquidity):
    #pot_token = "NO"  # Initialize variable to avoid reference errors
    updated_at = datetime.datetime.utcnow().isoformat()
    risk_score = await calculate_risk(marketCap, volume)
    
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            await conn.execute("""
                UPDATE tokens
                SET marketCap = ?, volume = ?, liquidity = ?, risk_score = ?, updated_at = ?
                WHERE token_address = ?
            """, (marketCap, volume, liquidity, risk_score, updated_at, token_address))
            await conn.commit()

        logger.info(f"✅ {token_address} updated: MarketCap: {marketCap}, Risk: {risk_score}")
    except Exception as e:
        logger.error(f"❌ Error updating {token_address}: {e}")


async def get_market_caps_from_db(token_address):
    """Fetch int_marketCap, marketCap, and timestamps for a token from the database."""
    async with aiosqlite.connect(DATABASE_NAME) as conn:
        cursor = await conn.execute(
            "SELECT int_marketCap, marketCap, initial_at, updated_at FROM tokens WHERE token_address = ?",
            (token_address,)
        )
        result = await cursor.fetchone()
    return result if result else (None, None, None, None)


async def holders_to_db(token_address, holders):
    """Update the holders count in the database for a given token."""
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            await conn.execute("""
                UPDATE tokens SET holders = ? WHERE token_address = ?
            """, (holders, token_address))
            await conn.commit()
        logger.info(f"✅ Holders count updated for {token_address}: {holders}")
    except Exception as e:
        logger.error(f"❌ Error updating holders count: {e}")

async def get_all_tokens():
    async with aiosqlite.connect(DATABASE_NAME) as conn:
        cursor = await conn.execute("SELECT token_address FROM tokens")
        rows = await cursor.fetchall()
    return [{"token_address": row[0]} for row in rows]


async def get_all_tokens2():
    async with aiosqlite.connect(DATABASE_NAME) as conn:
        cursor = await conn.execute("SELECT * FROM tokens")  # Fetch all columns
        rows = await cursor.fetchall()

    # Get column names dynamically
    async with aiosqlite.connect(DATABASE_NAME) as conn:
        cursor = await conn.execute("PRAGMA table_info(tokens)")
        columns = [col[1] for col in await cursor.fetchall()]  # Extract column names

    # Convert rows into a list of dictionaries
    return [dict(zip(columns, row)) for row in rows]

async def get_all_token_addresses():
    """Fetch all token addresses from the database."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        cursor = await db.execute("SELECT token_address FROM tokens")  # ✅ Adjust table if needed
        rows = await cursor.fetchall()
        await cursor.close()
        return [row[0] for row in rows] if rows else []