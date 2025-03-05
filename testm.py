import asyncio
import logging
from modules.core.format import format_number
from modules.database import get_all_tokens, get_all_token_addresses  # Fetch token addresses
from modules.market_data import get_token_data, get_volume_data, get_liquidity_data  # Fetch volume data


logger = logging.getLogger(__name__)

async def track_market():
    """Fetch MarketCap, holders, and volume for multiple tokens from DB and update separately."""
    while True:
        token_address = await get_all_token_addresses()  # ✅ Fetch tokens from database

        if not token_address:
            logger.warning("No tokens found in database. Retrying...")
            await asyncio.sleep(60)  # Wait before retrying
            continue

        # ✅ Batch API Calls - Fetch Data for ALL tokens at once
        marketCaps = await get_token_data(token_address)  
        volumes = await get_volume_data(token_address)  
        liquidities = await get_liquidity_data(token_address)  

        tasks = []  # Store async tasks

        for token in token_address:
            tasks.append(asyncio.create_task(process_token(token, marketCaps, volumes, liquidities)))

        # ✅ Run all token updates in parallel
        await asyncio.gather(*tasks)

        await asyncio.sleep(40)  # Re-check every 40 seconds

async def process_token(token_address, marketCaps, volumes, liquidities):
    """Processes each token individually by calling modular functions."""
    marketCap = marketCaps.get(token_address, "Not Available")
    volume = volumes.get(token_address, 0)
    liquidity = liquidities.get(token_address, 0)

    if marketCap == "Not Available" or float(marketCap) < 30000:
        return  # Skip low-market-cap tokens

    await save_to_db(token_address, marketCap, volume, liquidity)
    await check_graduation(token_address, marketCap)
    await log_and_notify(token_address, marketCap, volume, liquidity)

async def save_to_db(token_address, marketCap, volume, liquidity):
    """Handles database updates separately."""
    from modules.database import market_to_db  # ✅ Import only when needed to avoid circular imports
    await market_to_db(token_address, marketCap, volume, liquidity)

async def check_graduation(token_address, marketCap):
    """Handles logic for graduation to the next tier."""
    if float(marketCap) >= 57000:
        status = "Graduating"
        logger.info(f"🎓 {token_address} has crossed 60K! Moving to graduating_db")
        from modules.database import move_to_graduating_db
        await move_to_graduating_db(token_address, marketCap, status)

        # Apply degen classification
        from modules.filters import classify_degen  # ✅ Import classification function
        degen_category = await classify_degen(token_address)
        logger.info(f"🛠️ {token_address} classified as: {degen_category}")

async def log_and_notify(token_address, marketCap, volume, liquidity):
    """Handles logging and notifications separately."""
    logger.info(f"💰 {token_address} - MarketCap: ${format_number(marketCap)}, Volume: {format_number(volume)}")

    if liquidity < 10_000:
        print(f"⚠️ {token_address} - Low Liquidity: ${format_number(liquidity)}")
    else:
        print(f"✅ {token_address} - Total Liquidity: ${format_number(liquidity)}")

if __name__ == "__main__":
    asyncio.run(track_market())  # ✅ Starts tracking market data

