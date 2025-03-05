import sqlite3
import aiosqlite
import asyncio
import datetime
import logging
from modules.config import DATABASE_NAME, GRADUATING

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
            status TEXT DEFAULT 'active',  -- 'active', 'graduating', 'rugged', etc.
            risk_score TEXT DEFAULT 'Unknown',  -- ✅ Risk Category (Safe, Medium, High)
            pot_token TEXT DEFAULT NULL, -- ✅ Potential token flag
            holders REAL,  -- ✅ New column for holders
            xmade REAL,  -- ✅ New column for number of x made      
            initial_at TEXT DEFAULT CURRENT_TIMESTAMP,  -- ✅ Stores when token was first added
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP -- ✅ Store time when marketCap was updated

        )
    """)
    conn.commit()
    conn.close()


async def enable_wal_mode():
    """Enable WAL mode to prevent database locking issues."""
    async with aiosqlite.connect(GRADUATING) as conn:
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.commit()
    logger.info("✅ WAL mode enabled for graduating_tokens database.")

#--------------------------------------------------------

async def initialize_database():
    async with aiosqlite.connect(GRADUATING) as db:  # ✅ Use the same DB file
        await db.execute("""
            CREATE TABLE IF NOT EXISTS graduating_tokens (
                token_address TEXT PRIMARY KEY,
                twitter_link TEXT,
                risk_score TEXT DEFAULT 'Unknown',
                marketCap REAL,
                ath Real,
                trade TEXT,
                liquidity REAL DEFAULT 0,   
                holders INTEGER DEFAULT 0,
                volume REAL DEFAULT 0,
                degen REAL DEFAULT 0,
                pot_token TEXT DEFAULT NULL,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


"""
async def move_to_graduating_db(token_address, marketCap):
    #Move token to graduating DB and set pot_token if market cap > 140K.
    pot_token = "YES" if marketCap >= 140000 else "NO"  # ✅ Store "NO" instead of None
"""

async def move_to_graduating_db(token_address, marketCap):
    #from modules.volume_trend import get_volume_trend 
    """Move token to graduating DB and set pot_token if market cap > 140K."""
    #pot_token = "YES" if marketCap >= 140000 else "NO"
    #pot_token = 55000 if marketCap >= 55000 else "NO"
      # Check if market cap is within the range
    if 55000 <= marketCap <= 70000:
        pot_token = marketCap  # Set pot_token to marketCap
        message = f"Token: {token_address}\nMarket Cap: {marketCap}\nPot Token: {pot_token}"
        send_telegram_alert(message)  # Send the alert only when in range

    async with aiosqlite.connect(GRADUATING) as conn:
        await conn.execute("""
            INSERT INTO graduating_tokens (token_address, marketCap, pot_token) 
            VALUES (?, ?, ?)
            ON CONFLICT(token_address) DO UPDATE SET 
            marketCap = excluded.marketCap,
            pot_token = excluded.pot_token;
            
        """, (token_address, marketCap, pot_token))
        await conn.commit()
    
    await asyncio.sleep(0)  # ✅ Prevents deadlocks by allowing other tasks to run

    logger.info(f"✅ {token_address} saved/updated in graduating_db with marketCap: {marketCap}")

async def get_previous_marketCap(token_address):
    """Fetch the last stored market cap from the database asynchronously."""
    async with aiosqlite.connect(DATABASE_NAME) as conn:
        async with conn.execute("SELECT cur_marketCap FROM tokens WHERE token_address = ?", (token_address,)) as cursor:
            result = await cursor.fetchone()

    return result[0] if result else None


async def fetch_graduating_tokens():
    """Fetch token addresses, market caps, and ATH from graduating.db asynchronously."""
    async with aiosqlite.connect(GRADUATING) as conn:
        cursor = await conn.execute("SELECT token_address, marketCap, ath FROM graduating_tokens")
        tokens = await cursor.fetchall()

    #logger.info(f"📊 Raw Database Output: {tokens}")  # ✅ Log raw data

    # ✅ Ensure 'marketCap' and 'ath' are never None
    formatted_tokens = [
        (row[0], row[1] if row[1] is not None else 0, row[2] if row[2] is not None else 0)
        for row in tokens
    ]

  #  logger.info(f"📊 Processed Tokens: {formatted_tokens}")  # ✅ Log cleaned data
    return formatted_tokens


async def batch_update_graduating_tokens(updates):
    """Batch update market cap, volume, and pot_token for graduating tokens."""

    if not updates:
        return  # No updates to process
    
    try:
        conn = sqlite3.connect(GRADUATING)
        cursor = conn.cursor()
        cursor.executemany("""
            UPDATE graduating_tokens
            SET marketCap = ?, volume = ?, pot_token = ?, liquidity = ?, trade = ?, degen = ?, ath = ?
            WHERE token_address = ?
        """, updates)
        conn.commit()
        conn.close()
        logger.info(f"✅ Batch update successful for {len(updates)} tokens")
    except Exception as e:
        logger.error(f"❌ Batch update error: {e}")


def delete_graduating_token(token_address):
    """Delete a token from the graduating database."""
    try:
        conn = sqlite3.connect(GRADUATING)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM graduating_tokens WHERE token_address = ?", (token_address,))
        conn.commit()
        conn.close()
        logger.info(f"🗑️ Deleted {token_address} from graduating_db")
    except Exception as e:
        logger.error(f"❌ Error deleting token {token_address}: {e}")


async def save_to_db(token_name, token_address, twitter_link, int_marketCap, marketCap):
    """Asynchronously save token data to database."""
    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            cursor = await conn.cursor()
            await cursor.execute("""
                INSERT OR IGNORE INTO tokens (token_name, token_address, twitter_link, int_marketCap, marketCap) 
                VALUES (?, ?, ?, ?, ?)
            """, (token_name, token_address, twitter_link, int_marketCap, marketCap))
            await conn.commit()  # ✅ Use `await` for async commit

        logger.info(f"✅ Saved to DB: {token_name} - {token_address} - Market Cap: {int_marketCap} - Market: {marketCap}")
    except Exception as e:
        logger.error(f"❌ Database Error in save to db: {e}")


def calculate_risk(marketCap, volume):
    """Calculate risk score based on market cap and volume."""
    try:
        marketCap = float(marketCap)  # ✅ Ensure marketCap is a float
        volume = float(volume)        # ✅ Ensure volume is a float

        if marketCap >= 50000 and volume >= 10000:
            return "High Risk"
        elif marketCap >= 30000:
            return "Medium Risk"
        else:
            return "Low Risk"
    except ValueError:
        return "Invalid Data"  # ✅ Handles non-numeric values safely


async def market_to_db(token_address, marketCap, volume):
    """Asynchronously update MarketCap, Volume, and Risk Score."""
    updated_at = datetime.datetime.utcnow().isoformat()
    risk_score = calculate_risk(marketCap, volume)

    try:
        async with aiosqlite.connect(DATABASE_NAME) as conn:
            await conn.execute(
                """
                INSERT INTO tokens (token_address, marketCap, volume, risk_score, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(token_address) DO UPDATE 
                SET marketCap = excluded.marketCap, 
                    volume = excluded.volume, 
                    risk_score = excluded.risk_score, 
                    updated_at = excluded.updated_at;
                """,
                (token_address, marketCap, volume, risk_score, updated_at)
            )
            await conn.commit()
        
        logger.info(f"✅ {token_address} updated: MarketCap: {marketCap}, Risk: {risk_score}")
    
    except Exception as e:
        logger.error(f"❌ Error updating market cap for {token_address}: {e}")

   # print(f"✅ {token_address} updated: MarketCap: {marketCap}, Risk: {risk_score}")


def get_market_caps_from_db(token_address):
    """Fetch int_marketCap, marketCap, and timestamp for a token from the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT int_marketCap, marketCap, initial_at, updated_at FROM tokens WHERE token_address = ?",
        (token_address,)
    )
    
    result = cursor.fetchone()  # Fetch the row
    conn.close()

    if result:
        return result  # Returns (int_marketCap, marketCap, updated_at)
    else:
        return (None, None, None, None)  # Return None if no data found

import sqlite3

DB_FILE = "tokens.db"  # Change this to your actual database file

def holders_to_db(token_address, holders):
    """Update the holders count in the database for a given token."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE tokens SET holders = ? WHERE token_address = ?",
            (holders, token_address),
        )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Holders count updated for {token_address}: {holders}")

    except Exception as e:
        print(f"❌ Error updating holders count: {e}")


async def get_all_tokens():
    async with aiosqlite.connect(DATABASE_NAME) as conn:
        cursor = await conn.execute("SELECT token_address FROM tokens")
        rows = await cursor.fetchall()
    return [{"token_address": row[0]} for row in rows]


