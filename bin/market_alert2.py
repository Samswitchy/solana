import asyncio
import logging
from database import market_to_db, get_all_tokens, holders_to_db
from modules.market_data import get_token_data
from sivan.bin.holders2 import get_holders_count

logger = logging.getLogger(__name__)

async def track_market(token_address):
    """Fetch MarketCap and Holders Count every 40 seconds and update the database."""
    while True:
        try:
            # ✅ Ensure market data fetching doesn't block event loop
            marketCap = await asyncio.to_thread(get_token_data, token_address)

            # ✅ Fetch holders count
            #holders_count = await get_holders_count(token_address)
            #logger.info(f"🛠 Debug Holders for {token_address}: {holders_count}")
            tokens = get_all_tokens()  # Fetch all token addresses

            for token in tokens:  # token is already a string (not a dictionary)
                holders = await get_holders_count(token)  # Pass token directly
                print(f"Final Holders Count for {token}: {holders}")

            # ✅ Update MarketCap if valid
            if marketCap and marketCap != "Not Available":
                logger.info(f"💰 MarketCap Update for {token_address}: ${marketCap}")
                await market_to_db(token_address, marketCap)

           
        except Exception as e:
            logger.error(f"❌ Error tracking {token_address}: {e}")

        await asyncio.sleep(40)  # Wait 40 seconds before checking again

async def track_multiple_tokens():
    """Continuously fetch market data and holders count for newly added tokens."""
    tracked_tasks = {}

    while True:
        try:
            # ✅ Fetch token list in a non-blocking way
            tokens = await asyncio.to_thread(get_all_tokens)

            # ✅ Fix: Ensure tokens is a list of strings
            active_token_addresses = set(tokens)

            # ✅ Start tracking new tokens
            for token_address in active_token_addresses:
                if token_address not in tracked_tasks:
                    tracked_tasks[token_address] = asyncio.create_task(track_market(token_address))
                    logger.info(f"🚀 Started tracking {token_address}")

            # ✅ Stop tracking removed tokens
            for token_address in list(tracked_tasks.keys()):
                if token_address not in active_token_addresses:
                    tracked_tasks[token_address].cancel()
                    del tracked_tasks[token_address]
                    logger.info(f"🛑 Stopped tracking {token_address}")

        except Exception as e:
            logger.error(f"❌ Error in token tracking loop: {e}")

        await asyncio.sleep(120)  # Refresh token list every 2 minutes

# Run the tracking
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(track_multiple_tokens())
