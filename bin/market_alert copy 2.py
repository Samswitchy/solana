import asyncio
import logging
from modules.core.format import format_number
from modules.filters import classify_degen
from modules.database import (
    market_to_db,
    get_all_tokens,
    move_to_graduating_db,
    fetch_graduating_tokens,
    batch_update_tokens,
    inactive_to_db,
    delete_graduating_token
)

logger = logging.getLogger(__name__)

from modules.market_data import (
    get_token_data, get_holders_data, 
    get_volume_data ,
    get_holders_data,
    get_liquidity_data
 ) # ✅ Import holders & volume functions
#from trade.bmain import buy_tokens_if_needed

async def track_market(token_address):
    """Fetch MarketCap, holders, and volume for multiple tokens in one API call and update separately."""
    while True:
        #token_address = await get_all_tokens()  # ✅ Fetch tokens from database

        # ✅ Batch API Calls - Fetch Data for ALL tokens at once
        marketCaps = await get_token_data(token_address)  # Returns
        volumes = await get_volume_data(token_address)  # Returns {token: volume}
        liquidities = await get_liquidity_data(token_address)  # Returns {token: liquidity}

        tasks = []  # Store async tasks for concurrent execution

        for token in token_address:
            # Get individual token data
            marketCap = marketCaps.get(token, "Not Available")
            volume = volumes.get(token, 0)
            liquidity = liquidities.get(token, 0)

            # ✅ Each token updates separately in its own task
            tasks.append(asyncio.create_task(update_token(token, marketCap, volume, liquidity)))

        # ✅ Run all token updates in parallel
        await asyncio.gather(*tasks)

        await asyncio.sleep(20)  # Re-check every 40 seconds

async def update_token(token_address, marketCap, volume, liquidity):
    """Process and update a single token's data separately."""
    if marketCap == "Not Available":
        return  

    marketCap = float(marketCap)

    if marketCap < 30000:
        return  # Skip this token

    status = "Active"
    logger.info(f"💰 {token_address} - MarketCap: ${format_number(marketCap)}, Volume: {format_number(volume)}")

    await market_to_db(token_address, marketCap, volume, liquidity)  # ✅ Save to DB separately

    if marketCap >= 57000:
        status = "Graduating"
        logger.info(f"🎓 {token_address} has crossed 57K! Moving to graduating_db")
        await move_to_graduating_db(token_address, marketCap, status)

        degen_category = await classify_degen(token_address)
        logger.info(f"🛠️ {token_address} classified as: {degen_category}")

    if liquidity < 10_000:
        print(f"⚠️ {token_address} - Low Liquidity: ${format_number(liquidity)}")
    else:
        print(f"✅ {token_address} - Total Liquidity: ${format_number(liquidity)}")

# Example usage:
# asyncio.run(track_tokens(["TOKEN1", "TOKEN2", "TOKEN3"]))
#-----------------------------------------------------------------------------------

async def track_graduating_tokens():
    """Track tokens already in graduating.db and update their market cap."""
    while True:
        try:
            tokens = await fetch_graduating_tokens()  # ✅ Ensure it returns prev_ath & prev_marketCap

            if tokens:
                updates = []
                for token_address, prev_marketCap, prev_ath in tokens:
                    new_marketCap = await get_token_data(token_address) or "Not Available"
                    new_volume = await get_volume_data(token_address) or 0
                    new_liquidity = await get_liquidity_data(token_address) or 0


                    if new_marketCap != "Not Available":
                        new_marketCap = float(new_marketCap)

                        # ✅ Ensure ATH updates correctly
                        new_ath = max(prev_ath or 0, new_marketCap)

                        # ✅ Classify token
                        degen = new_marketCap if new_marketCap >= 100000 else 0

                        # ✅ Set trade condition
                        # ✅ Update `pot_token` if marketCap is between 55K and 70K
                        pot_token = new_marketCap if 55000 <= new_marketCap <= 70000 else "NO"
                        
                        liquidity_status = new_liquidity if new_liquidity >= 20000 else "NO"

                        trade = "BUY" if 58000 <= new_marketCap <= 70000 and liquidity_status != "NO" else "HOLD"

                        if new_marketCap > prev_marketCap or new_marketCap >= 55000:
                            updates.append((
                                new_marketCap,
                                new_volume, 
                                pot_token, 
                                liquidity_status, 
                                trade, 
                                degen, 
                                new_ath, 
                                token_address
                            ))
                        elif new_marketCap < 13000:  # ✅ If below 10K, delete from graduating DB
                            logger.warning(f"🚨 {token_address}Token below 15K! Deleting from DB.")
                            await delete_graduating_token(token_address)  # ✅ Ensure it's awaited
                        elif new_marketCap < 25000:
                            status = "Inactive"
                            logger.warning(f"⚠️ {token_address}Token below 25K! Inactive in Status.")
                            await inactive_to_db(token_address,status)  # ✅ Ensure it's awaited
                        
                            #

                if updates:
                    try:
                        await batch_update_tokens(updates)  # ✅ Awaiting the update
                        logger.info(f"✅ Successfully updated {len(updates)} graduating tokens.")
                    except Exception as e:
                        logger.error(f"❌ Failed to update graduating tokens: {e}")

            await asyncio.sleep(20)

        except Exception as e:
            logger.error(f"❌ Error in track_graduating_tokens: {e}")
            await asyncio.sleep(10)  # Retry after 10s

async def track_multiple_tokens():
    """Continuously fetch market data for newly added tokens."""
    tracked_tasks = {}

    while True:
        tokens_data = await get_all_tokens()  # ✅ Await the async function
        tokens = set(token["token_address"] for token in tokens_data)  # ✅ Now it works

        # ✅ Stop tracking removed tokens
        for token_address in list(tracked_tasks.keys()):
            if token_address not in tokens:
                tracked_tasks[token_address].cancel()
                del tracked_tasks[token_address]
                logger.info(f"🛑 Stopped tracking {token_address}")

        # ✅ Start tracking new tokens
        for token_address in tokens:
            if token_address not in tracked_tasks:
                tracked_tasks[token_address] = asyncio.create_task(track_market(token_address))
                logger.info(f"🚀 Started tracking {token_address}")

        await asyncio.sleep(30)  # ✅ Refresh token list every 80 seconds

async def classify_all_tokens():
    """Fetch token data and classify each token"""
    tokens = await get_all_tokens()  # ✅ Await the async function

    for token in tokens:
        token_address = token["token_address"]
        degen_category = classify_degen(token_address)  # Call the classification function
        logger.info(f"Token: {token_address}, Category: {degen_category}")  # Log instead of print