import asyncio
import logging
from modules.database import fetch_graduating_tokens, market_to_db, get_all_tokens, update_graduating_marketcap, delete_graduating_token

from modules.market_data import get_token_data
#form x import fetch_market_caps()

logger = logging.getLogger(__name__)

async def track_graduating_tokens():
    """Regularly check all tokens in graduating_db and update market cap."""
    while True:
        tokens = fetch_graduating_tokens()  # ✅ Get all tokens from database

        for token_address, prev_marketCap in tokens:
            new_marketCap = get_token_data(token_address)

            if new_marketCap != "Not Available":
                new_marketCap = float(new_marketCap)

                if new_marketCap > prev_marketCap:
                    logger.info(f"🚀 {token_address} has increased further! {prev_marketCap} → {new_marketCap}")

                    # ✅ Call function from database.py instead of writing SQL here
              
                    update_graduating_marketcap(token_address, new_marketCap)

                elif new_marketCap < 60000:  # Optional: Remove tokens that drop below 60K
                    logger.warning(f"⚠️ {token_address} has dropped below 60K! Removing from graduating_db.")
                     # ✅ Call function from database.py instead of writing SQL here
                    delete_graduating_token(token_address)
        
        await asyncio.sleep(60)  # Check every 60 seconds

async def track_multiple_tokens():
    """Continuously fetch market data for newly added tokens."""
    tracked_tasks = {}  # Dictionary to keep track of running tasks

    while True:
        tokens = get_all_tokens()
        
        active_token_addresses = {token["token_address"] for token in tokens}  # Extract token addresses

        # ✅ Start tracking new tokens
        for token_address in active_token_addresses:
            if token_address not in tracked_tasks:  # Only track if not already being tracked
                tracked_tasks[token_address] = asyncio.create_task(track_market(token_address))
                logger.info(f"🚀 Started tracking {token_address}")

        # ✅ Stop tracking removed tokens
        for token_address in list(tracked_tasks.keys()):  # Iterate over existing tracked tokens
            if token_address not in active_token_addresses:  # If token was removed from the database
                tracked_tasks[token_address].cancel()  # Cancel the tracking task
                del tracked_tasks[token_address]
                logger.info(f"🛑 Stopped tracking {token_address}")

        await asyncio.sleep(80)  # Refresh token list every 2 minutes
