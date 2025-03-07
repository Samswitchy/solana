import asyncio
import logging
from telethon import TelegramClient, events
from modules.config import API_ID, API_HASH, PHONE_NUMBER, CHANNEL_USERNAME , TELEGRAM_DATA
from modules.core.extractor import extract_token_name, extract_token_address, extract_x_link
from modules.market_data import get_token_data
from modules.database import save_to_db
from modules.holders2 import get_holders_count
#from price_tracker import get_token_price
#from market_tracker import get_token_market


logger = logging.getLogger(__name__)

# ✅ Ensure an event loop exists before initializing the Telegram client
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

client = TelegramClient(TELEGRAM_DATA, API_ID, API_HASH)

async def process_message(message_text):
    try:
        token_name = extract_token_name(message_text)
        token_address = extract_token_address(message_text)
        twitter_link = extract_x_link(message_text)
        # Example token address
        #TOKEN_ADDRESS = "AVrNeiU54AdXxvpHXkjrMZfpM1v22ZYU94urYH6cpump"
        #TOKEN_ADDRESS = 

        # Fetch holders count
        #holders = get_holders_count(token_address)
        """
        tokens = token_address
        holders = await get_holders_count(tokens)
        # Print the result
        if holders:
            print(f"✅ Holders Count for {token_address}: {holders}")
        else:
            print(f"❌ Could not extract holders count for {token_address}")
        """
        if token_address:
            #marketCap = await asyncio.to_thread(get_token_data, token_address)  # Run API call in background
            #marketCap, holders = await asyncio.gather(
            #asyncio.to_thread(get_token_data, token_address),  # Fetch market cap
            #get_holders_count(token_address)  # Fetch holders count
            #)           
            marketCap, holders = await asyncio.gather(
            get_token_data(token_address),  # ✅ Directly await async function
            get_holders_count(token_address)  # ✅ Directly await async function
            )

            int_marketCap = marketCap  # Convert marketCap to an integer if needed
            
            ath = marketCap

            logger.info(f"✅ Extracted Address: {token_address}")
            logger.info(f"✅ Extracted Market Cap: {marketCap}")
            logger.info(f"✅ All-Time High (ATH): {ath}")

            if twitter_link:
                logger.info(f"✅ Extracted X Link: {twitter_link}")

            # ✅ Save to database asynchronously
            #await asyncio.to_thread(save_to_db, token_name, token_address, twitter_link, int_marketCap, marketCap)
            #await asyncio.to_thread(save_to_db, token_name, token_address, twitter_link, int_marketCap, marketCap)
             # ✅ Save to database asynchronously (NO NEED FOR `asyncio.to_thread`)
            await save_to_db(token_name, token_address, twitter_link, int_marketCap, marketCap, ath)

    except Exception as e:
        logger.error(f"❌ Error in process_message: {e}")


@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handle_new_message(event):
    try:
        asyncio.create_task(process_message(event.message.text))
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")

async def run_telegram_client():
    try:
        logger.info("🚀 Connecting to Telegram...")
        await client.start(PHONE_NUMBER)
        logger.info("🟢 Connected and listening...")
        logger.info("📩 Client is running. Waiting for new messages...")
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"❌ Error: {e}. Reconnecting...")
