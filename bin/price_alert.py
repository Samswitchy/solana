import asyncio
import logging
from database import save_to_db
from price_tracker import get_token_price

logger = logging.getLogger(__name__)

async def track_price(token_address):
    """Fetches price every 60 seconds and logs it."""
    while True:
        price = get_token_price(token_address)
        if price != "Not Available":
            logger.info(f"💰 Price Update for {token_address}: ${price}")
            save_to_db(None, token_address, None, None, price)  # Update DB price
        await asyncio.sleep(60)  # ✅ Fetch price every 60 seconds


