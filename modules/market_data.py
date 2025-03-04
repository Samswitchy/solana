import aiohttp
import logging
import asyncio
import time
from modules.database import get_all_tokens, holders_to_db  # ✅ Import holders_to_db
from modules.holders2 import get_holders_count  # ✅ Import function from holders2.py

logger = logging.getLogger(__name__)


semaphore = asyncio.Semaphore(3)  # Limit concurrent API calls
cache = {}  # Cache to store API responses

async def fetch_json(url, retries=5, delay=2):
    """Fetch JSON data with exponential backoff, rate limiting, and caching."""
    async with semaphore:
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 429:
                            retry_after = int(response.headers.get("Retry-After", delay))
                            logger.warning(f"⚠️ Rate limited! Retrying in {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                            continue

                        response.raise_for_status()
                        return await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"API request failed: {e}")
                await asyncio.sleep(delay * (attempt + 1))
        return None

async def get_token_data(token_address):
    """Fetch market cap data with caching."""
    if token_address in cache and time.time() - cache[token_address]["timestamp"] < 60:
        return cache[token_address]["marketCap"]  # Use cached data if less than 60s old

    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    data = await fetch_json(url)

    if data and "pairs" in data and isinstance(data["pairs"], list) and len(data["pairs"]) > 0:
        market_cap = float(data["pairs"][0].get("marketCap", 0))
        cache[token_address] = {"marketCap": market_cap, "timestamp": time.time()}
        return market_cap
    return 0

async def get_volume_data(token_address):
    """Fetch 24h trading volume across all DEX pairs asynchronously."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    data = await fetch_json(url)
    
    if data and "pairs" in data and isinstance(data["pairs"], list):
        total_volume = sum(
            float(pair.get("volume", {}).get("h24", 0))
            for pair in data["pairs"]
            if float(pair.get("liquidity", {}).get("usd", 0)) > 500
        )
        return total_volume if total_volume > 0 else 0
    return 0

async def get_liquidity_data(token_address):
    """Fetch total liquidity across all DEX pairs for a given token asynchronously."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    data = await fetch_json(url)

    if data and "pairs" in data and isinstance(data["pairs"], list):
        total_liquidity = sum(
            float(pair.get("liquidity", {}).get("usd", 0))
            for pair in data["pairs"]
            if float(pair.get("liquidity", {}).get("usd", 0)) > 500
        )
        return total_liquidity if total_liquidity > 0 else 0
    return 0


async def get_holders_data():
    """Fetch holders count for all tokens and update the database asynchronously."""
    tokens = get_all_tokens()  # Fetch all token addresses

    for token in tokens:
        holders_count = await get_holders_count(token["token_address"])  # ✅ Now async
        logger.info(f"✅ Extracted Holders Count: {holders_count}")

        if holders_count and holders_count != "Not Available":
            logger.info(f"👥 Holders Count Updated for {token['token_address']}: {holders_count}")
            await holders_to_db(token["token_address"], holders_count)  # ✅ Now async
        else:
            logger.warning(f"⚠️ Skipping update for {token['token_address']}, holders count unavailable.")


async def get_trending_data(token_address):
    """Fetch full trending data with caching."""
    if token_address in cache and time.time() - cache[token_address]["timestamp"] < 60:
        return cache[token_address]["data"]  # Return full cached data

    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    data = await fetch_json(url)

    if data and "pairs" in data and isinstance(data["pairs"], list) and len(data["pairs"]) > 0:
        cache[token_address] = {"data": data, "timestamp": time.time()}
        return data  # ✅ Now returning full token data
    return None
