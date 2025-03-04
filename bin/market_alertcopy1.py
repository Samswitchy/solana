import asyncio
import logging
from modules.database import (
    market_to_db,
    get_all_tokens,
    move_to_graduating_db,
    fetch_graduating_tokens,
    update_graduating_marketcap,
    delete_graduating_token,
)
from modules.market_data import get_token_data, get_volume_data

logger = logging.getLogger(__name__)

from modules.market_data import (
    get_token_data, get_holders_data, 
    get_volume_data ,
    #get_holders_data,
 ) # ✅ Import holders & volume functions

async def track_market(token_address):
    """Fetch MarketCap, holders, and volume every 60 seconds and update the database."""
    while True:
        marketCap, twitter_link = get_token_data(token_address)
        #holders = get_holders_data(token_address)
        volume = get_volume_data(token_address)

        if marketCap != "Not Available":
            marketCap = float(marketCap)

            if marketCap >= 30000:
                #logger.info(f"💰 {token_address} - MarketCap: ${marketCap}, Holders: {holders}, Volume: {volume}")
                logger.info(f"💰 {token_address} - MarketCap: ${marketCap}, Holders: , Volume: {volume}")
                await market_to_db(token_address, marketCap)

            if marketCap >= 65000:
                logger.info(f"🎓 {token_address} has crossed 60K! Moving to graduating_db")
                await move_to_graduating_db(token_address, marketCap, twitter_link)  # ✅ Move to graduating DB
        
        await asyncio.sleep(40)  # Check every 40 seconds


async def track_graduating_tokens():
    """Track tokens already in graduating.db and update their market cap."""
    while True:
        tokens = fetch_graduating_tokens()  # Get tokens from graduating_db

        for token_address, prev_marketCap in tokens:
            new_marketCap = get_token_data(token_address)
            #new_holders = get_holders_data(token_address)  # Get updated holders
            new_volume = get_volume_data(token_address)  # Get updated volume

            if new_marketCap != "Not Available":
                new_marketCap = float(new_marketCap)

                if new_marketCap > prev_marketCap:
                    logger.info(f"🚀 {token_address} increased: {prev_marketCap} → {new_marketCap}")
                    #update_graduating_marketcap(token_address, new_marketCap, new_holders, new_volume)  # ✅ Update DB
                    update_graduating_marketcap(token_address, new_marketCap, new_volume)  # ✅ Update DB

                elif new_marketCap < 60000:  # Remove if below 60K
                    logger.warning(f"⚠️ {token_address} dropped below 60K! Removing from graduating_db.")
                    delete_graduating_token(token_address)  # ✅ Remove from DB
        
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
        for token_address in list(tracked_tasks.keys()):  
            if token_address not in active_token_addresses:  
                tracked_tasks[token_address].cancel()  # Cancel the tracking task
                del tracked_tasks[token_address]
                logger.info(f"🛑 Stopped tracking {token_address}")

        await asyncio.sleep(80)  # Refresh token list every 2 minutes
