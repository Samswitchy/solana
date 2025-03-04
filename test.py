import asyncio
import logging
from modules.database import get_all_tokens, holders_to_db  # ✅ Import holders_to_db
from modules.holders2 import get_holders_count  # ✅ Import function from holders2.py

# ✅ Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def main():
    tokens = get_all_tokens()  # Fetch all token addresses

    for token in tokens:
        holders_count = await get_holders_count(token)  # Fetch holders count

        # ✅ Update Holders Count if available
        if holders_count and holders_count != "Not Available here 2":
            #print("Holders Count Update for" {token}, ",{holders_count})
            print(f"✅ Holders Count for {token}: {holders_count}")
            #logger.info(f"👥 Holders Count Update for {token}: {holders_count}")
            #await holders_to_db(token, holders_count)  # ✅ Store in database

        else:
            logger.warning(f"⚠️ Skipping update for {token}, holders count unavailable.")

# ✅ Run the async function
asyncio.run(main())
