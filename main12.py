import asyncio
import logging
from database import init_db, get_all_tokens  # Import get_all_tokens
from telegram_client import run_telegram_client
from modules.market_data import get_token_data
#from price_alert import track_price
from market_alert import track_market

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    init_db()  # Ensure database is initialized

    # ✅ Dynamically fetch tokens from the database
    token_list = get_all_tokens()
    
    if not token_list:
        logging.warning("⚠️ No tokens found in database. Add some first!")

    
    marketCap = [track_market(token) for token in token_list]
    
    await asyncio.gather(run_telegram_client(), *marketCap)

if __name__ == "__main__":
    asyncio.run(main())
