import asyncio
import logging
from modules.database import init_db, get_all_tokens,fetch_graduating_tokens
from telegram_client import run_telegram_client
#from market_alert import track_market
from market_alert import track_market, track_multiple_tokens, track_graduating_tokens
from modules.holders2 import get_holders_count
from market_alert import classify_all_tokens

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def track_all_tokens(): 
    """Dynamically tracks market caps for all tokens in the database."""
    tracked_tasks = {}

    while True:
        token_list = await get_all_tokens()  # ✅ Await the async function

        for token in token_list:
            token_address = token["token_address"]  # ✅ Extract token address
            
            if token_address not in tracked_tasks:  # ✅ Use token_address instead of dict
                tracked_tasks[token_address] = asyncio.create_task(track_market(token_address))
        
        await asyncio.sleep(70)  # Refresh token list every 2 minutes
"""
async def track_holders():
    #Tracks holders count for each token in the database.
    while True:
        token_list = get_all_tokens()

        for token in token_list:
            holders = await get_holders_count(token)
            if holders:
                logging.info(f"✅ {token} - Holders Count: {holders}")
            else:
                logging.warning(f"❌ Could not extract holders count for {token}")

        await asyncio.sleep(180)  # Refresh holders count every 3 minutes
"""
"""
async def main():
    init_db()  # Ensure database is initialized
    
    # ✅ Run tasks concurrently using create_task()
    asyncio.create_task(run_telegram_client())  # Run Telegram client
    asyncio.create_task(track_all_tokens())  # Track market data
    asyncio.create_task(track_multiple_tokens())  # Track market data
    asyncio.create_task(track_graduating_tokens())  # ✅ Add this line to track graduating tokens

    #asyncio.create_task(track_holders())  # Track holders count

    while True:
        await asyncio.sleep(5)  # Prevents main from exiting

if __name__ == "__main__":
    #asyncio.run(main())
    loop = asyncio.new_event_loop()  # ✅ Create a new event loop
    asyncio.set_event_loop(loop)  
    loop.run_until_complete(main())  # ✅ Run the main function inside the new loop



"""

async def main():
    init_db()
    #await initialize_database()  # ✅ Ensure table exists
    #asyncio.run(initialize_db())
    tokens = await fetch_graduating_tokens()
    #await client.start()  # Ensure Telegram client is started properly
    asyncio.create_task(track_all_tokens())
    asyncio.create_task(track_multiple_tokens())
    asyncio.create_task(track_graduating_tokens())
    #await classify_all_tokens()  # ✅ Ensure it runs properly inside an a
    await run_telegram_client()  # Run the Telegram client properly

if __name__ == "__main__":
    asyncio.run(main())