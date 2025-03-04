import requests
import aiohttp
import logging
import asyncio
import sqlite3
import time
from modules.config import TRADE

logger = logging.getLogger(__name__)

def get_token_marketcap(mint):
    """Fetches the latest price and market cap from Dex Screener."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "pairs" in data and len(data["pairs"]) > 0:
            market_cap = float(data["pairs"][0]["fdv"])  # FDV = Market Cap
            price = float(data["pairs"][0]["priceUsd"])  # Get token price
            
            return price, market_cap  # ✅ Always return two values
        else:
            print(f"❌ No market cap data found for {mint}.")
            return None, None  # ✅ Ensure two values are always returned
    except Exception as e:
        print(f"❌ Error fetching market cap: {e}")
        return None, None  # ✅ Return None for both if error occurs

def update_marketcap():
    """Updates new market cap and timestamp if it changes."""
    updated_at = datetime.datetime.utcnow().isoformat()
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


async def fetch_json(url):
    """Helper function to fetch JSON data asynchronously."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"API request failed: {e}")
        return None

async def get_token_data(token_address):
    """Fetch market cap data from DexScreener API asynchronously."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    data = await fetch_json(url)
    if data and "pairs" in data and isinstance(data["pairs"], list) and len(data["pairs"]) > 0:
        pair = data["pairs"][0]
        return float(pair.get("marketCap", 0))  # Convert to float
    return 0  # Return 0 instead of "Not Available"
