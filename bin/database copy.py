import sqlite3
import aiosqlite
import datetime
import logging
from modules.config import DATABASE_NAME, GRADUATING

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
            volume REAL DEFAULT 0, -- ✅ Trading volume
            degen TEXT DEFAULT NULL, -- ✅ degen token flag
            pot_token TEXT DEFAULT NULL, -- ✅ Potential token flag
            holders REAL,  -- ✅ New column for price
            initial_at TEXT DEFAULT CURRENT_TIMESTAMP,  -- ✅ Stores when token was first added
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP -- ✅ Store time when marketCap was updated

        )
    """)
    conn.commit()
    conn.close()

    # ✅ Initialize the graduating tokens database
    conn = sqlite3.connect(GRADUATING)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS graduating_tokens (
            token_address TEXT PRIMARY KEY,
            twitter_link TEXT,
            marketCap REAL,
            holders INTEGER DEFAULT 0, -- ✅ Holders count
            volume REAL DEFAULT 0, -- ✅ Trading volume
            degen TEXT DEFAULT NULL, -- ✅ degen token flag
            pot_token TEXT DEFAULT NULL, -- ✅ Potential token flag
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

async def move_to_graduating_db(token_address, marketCap, twitter_link):
    """Move token to graduating DB and set pot_token if market cap > 160K."""
    pot_token = "YES" if marketCap >= 160000 else None

    async with aiosqlite.connect(GRADUATING) as conn:
        await conn.execute("""
            INSERT INTO graduating_tokens (token_address, marketCap, twitter_link, pot_token) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(token_address) DO UPDATE SET 
            marketCap = excluded.marketCap,
            twitter_link = excluded.twitter_link,
            pot_token = excluded.pot_token;
        """, (token_address, marketCap, twitter_link, pot_token))
        await conn.commit()

           # ✅ Log success
        logger.info(f"✅ {token_address} saved/updated in graduating_db with marketCap: {marketCap}")

async def get_previous_marketCap(token_address):
    """Fetch the last stored market cap from the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT cur_marketCap FROM tokens WHERE token_address = ?", (token_address,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def fetch_graduating_tokens():
    """Fetch all tokens and their market caps from graduating_db."""
    conn = sqlite3.connect(GRADUATING)
    cursor = conn.cursor()

    cursor.execute("SELECT token_address, marketCap FROM graduating_tokens")
    tokens = cursor.fetchall()

    conn.close()
    return tokens  # ✅ Returns a list of (token_address, marketCap)

def update_graduating_marketcap(token_address, new_marketCap, volume, twitter_link,):
    """Update the market cap and set pot_token if above 160K."""
    pot_token = new_marketCap if new_marketCap >= 160000 else None  # ✅ Update pot_token

    try:
        conn = sqlite3.connect(GRADUATING)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE graduating_tokens 
            SET marketCap = ?, volume = ?, twitter_link = ?, pot_token = ? 
            WHERE token_address = ?
        """, (new_marketCap, volume, twitter_link, pot_token, token_address))

        conn.commit()
        conn.close()
        logger.info(f"✅ Updated {token_address} - Market Cap: {new_marketCap} - Potential: {pot_token} - Volume: {volume}")
    except Exception as e:
        logger.error(f"❌ Error updating graduating market cap: {e}")
    

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


def save_to_db(token_name, token_address, twitter_link, int_marketCap, marketCap):
#def save_to_db(token_name, token_address, twitter_link, int_marketCap):
    """Save token data to database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO tokens (token_name, token_address, twitter_link, int_marketCap, marketCap) 
            VALUES (?, ?, ?, ?,?)
        """, (token_name, token_address, twitter_link, int_marketCap, marketCap))
        conn.commit()
        logger.info(f"✅ Saved to DB: {token_name} - {token_address} - Market Cap: {int_marketCap} - Market: {marketCap}")
        #logger.info(f"✅ Saved to DB: {token_name} - {token_address} - Market Cap: {int_marketCap}")
    except Exception as e:
        logger.error(f"❌ Database Error: {e}")
    finally:
        conn.close()

async def market_to_db(token_address, marketCap):
    """Asynchronously update or insert MarketCap and timestamp for a given token."""
    updated_at = datetime.datetime.utcnow().isoformat()

    #print(f"Updating {token_address}: MarketCap = {marketCap}, updated_at = {updated_at}")
    print(f"Updating {token_address}: MarketCap = {marketCap}")

    async with aiosqlite.connect(DATABASE_NAME) as conn:
        await conn.execute(
            """
            INSERT INTO tokens (token_address, marketCap, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(token_address) DO UPDATE 
            SET marketCap = excluded.marketCap, updated_at = excluded.updated_at;
            """,
            (token_address, marketCap, updated_at)
        )
        await conn.commit()

    print("✅ Database update successful! on MarketCap")


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

def holders_to_db(token_address, holders_count):
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
        
        print(f"✅ Holders count updated for {token_address}: {holders_count}")

    except Exception as e:
        print(f"❌ Error updating holders count: {e}")

"""
def get_all_tokens():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT token_address FROM tokens")
    tokens = [row[0] for row in cursor.fetchall()]
    conn.close()  # ✅ Close the connection after each query
    return tokens
"""

def get_all_tokens():
    conn = sqlite3.connect(DATABASE_NAME)  # Ensure you're using the correct DB
    cursor = conn.cursor()
    
    cursor.execute("SELECT token_address FROM tokens")  
    rows = cursor.fetchall()  # Returns list of tuples [(address,), (address,)]
    
    conn.close()
    
    return [{"token_address": row[0]} for row in rows]  # Convert tuples to dictionaries
