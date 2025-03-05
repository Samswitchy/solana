import sqlite3
import aiosqlite
import asyncio
import requests
import sys
import os
# Go two levels up if needed
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Now, we can import config correctly
from modules.config import DATABASE_NAME, TRADE
from trade.core.config import HELIUS_RPC_URL, PRIVATE_KEY

#DB_PATH = "graduating.db"
DB_PATH = DATABASE_NAME

def create_table():
    """Ensures the database has the correct structure."""
    conn = sqlite3.connect(TRADE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bought_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_address TEXT UNIQUE,
            amount REAL,
            tx_signature TEXT,
            market_price REAL,
            market_cap REAL,
            new_marketcap REAL,
            x_made TEXT,
            x_sold TEXT,
            bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database schema verified.")
# ✅ Call this function at the start of your bot to ensure the table exists
create_table()

def get_mint_address():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT token_address FROM tokens  WHERE status = 'Graduating'")
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]
        else:
            print("No token address found in the database.")
            return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def save_bought_token(mint, amount, tx_signature, price, market_cap):
    """Saves token details when bought."""
    try:
        conn = sqlite3.connect(TRADE)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO bought_tokens (token_address, amount, tx_signature, market_price, market_cap, new_marketcap)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (mint, amount, tx_signature, price, market_cap, market_cap))

        conn.commit()
        conn.close()
        print(f"✅ Saved {mint} with price ${price} and market cap ${market_cap}.")
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

def fetch_info():
    """Fetches all tokens with their pot_token and marketcap from the graduating database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT token_address, pot_token, marketcap, trade FROM tokens WHERE status = 'Graduating' ")
        results = cursor.fetchall()  # ✅ Fetch all records
        conn.close()
        return results  # ✅ List of (TOKEN_MINT, POT_TOKEN, MARKETCAP) tuples
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    

def fetch_bought_tokens():
    """Fetch tokens that have been bought but not yet sold."""
    try:
        conn = sqlite3.connect(TRADE)
        cursor = conn.cursor()
        cursor.execute("SELECT token_address, amount, market_price, market_cap FROM bought_tokens WHERE x_sold IS NULL")
        tokens = cursor.fetchall()
        conn.close()
        return tokens  # Returns list of (TOKEN_MINT, AMOUNT, BUY_PRICE, BUY_MARKETCAP)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def get_token_balance(wallet_address: str, token_mint: str):
    """
    Fetch the token balance from the Solana blockchain.
    """
    client = Client(HELIUS_RPC_URL)
    balance_url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/balances?api-key=YOUR_API_KEY"
    
    response = requests.get(balance_url)
    if response.status_code != 200:
        print(f"❌ Error fetching balance: {response.status_code} - {response.text}")
        return None

    balances = response.json().get("tokens", [])
    
    for token in balances:
        if token["mint"] == token_mint:
            return token["amount"] / 10**token.get("decimals", 6)  # Normalize the balance

    return 0  # If token is not found, assume balance is 0

def get_market_caps_from_db(token_address):
    """Fetch int_marketCap, marketCap, and timestamp for a token from the database."""
    conn = sqlite3.connect(TRADE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT market_cap, new_marketcap, bought_at, updated_at FROM bought_tokens WHERE token_address = ?",
        (token_address,)
    )
    
    result = cursor.fetchone()  # Fetch the row
    conn.close()

    if result:
        return result  # Returns (int_marketCap, marketCap, updated_at)
    else:
        return (None, None, None, None)  # Return None if no data found

async def get_all_tokens():
    async with aiosqlite.connect(TRADE) as conn:
        cursor = await conn.execute("SELECT token_address FROM bought_tokens")
        rows = await cursor.fetchall()
    return [{"token_address": row[0]} for row in rows]


