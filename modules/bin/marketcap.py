import requests
import sqlite3
from config import TRADE

def get_token_marketcap(mint):
    """Fetches the latest market cap from Dex Screener."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "pairs" in data and len(data["pairs"]) > 0:
            return float(data["pairs"][0]["fdv"])  # FDV = Market Cap
        else:
            print(f"❌ No market cap data found for {mint}.")
            return None
    except Exception as e:
        print(f"❌ Error fetching market cap: {e}")
        return None

def update_marketcap():
    """Updates new market cap and timestamp if it changes."""
    conn = sqlite3.connect(TRADE)
    cursor = conn.cursor()

    cursor.execute("SELECT mint_address, new_marketcap FROM bought_tokens")
    tokens = cursor.fetchall()

    for mint, old_marketcap in tokens:
        new_marketcap = get_token_marketcap(mint)
        
        if new_marketcap and new_marketcap != old_marketcap:
            cursor.execute('''
                UPDATE bought_tokens
                SET new_marketcap = ?, updated_at = CURRENT_TIMESTAMP
                WHERE mint_address = ?
            ''', (new_marketcap, mint))
            
            print(f"✅ Updated {mint}: New Market Cap = ${new_marketcap}")

    conn.commit()
    conn.close()
    print("✅ Market cap updates complete.")
