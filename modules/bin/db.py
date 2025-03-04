import sqlite3

from config import GRADUATING, TRADE


#DB_PATH = "graduating.db"
DB_PATH = GRADUATING

def create_table():
    """Ensures the database has the correct structure."""
    conn = sqlite3.connect(TRADE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bought_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mint_address TEXT UNIQUE,
            amount REAL,
            tx_signature TEXT,
            market_price REAL,
            market_cap REAL,
            new_marketcap REAL,
            xmade TEXT,
            bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,-
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database schema verified.")




def get_mint_address():
    try:
        conn = sqlite3.connect(GRADUATING)
        cursor = conn.cursor()
        cursor.execute("SELECT token_address FROM graduating_tokens")
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
            INSERT OR REPLACE INTO bought_tokens (mint_address, amount, tx_signature, market_price, market_cap, new_marketcap)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (mint, amount, tx_signature, price, market_cap, market_cap))

        conn.commit()
        conn.close()
        print(f"✅ Saved {mint} with price ${price} and market cap ${market_cap}.")
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

