import asyncio
import logging
from modules.core.format import format_number
from modules.filters import classify_degen
from modules.database import get_all_tokens
from modules.database import (
    market_to_db,
    get_all_tokens,
    move_to_graduating_db,
    fetch_graduating_tokens,
    batch_update_tokens,
    delete_graduating_token,
)
from modules.market_data import (
    get_token_data,
    get_holders_data,
     get_liquidity_data, 
    get_volume_data 
 ) # ✅ Import holders & volume functions
logger = logging.getLogger(__name__)


#from trade.bmain import buy_tokens_if_needed


async def track_market():
    """Fetch MarketCap, holders, and volume every 60 seconds and update the database."""
    #logger.info(f"🔄 Tracking started for {token_address}")  # ✅ Log before looping

    while True:
        try:
            tokens = await fetch_graduating_tokens()  # ✅ Ensure it returns prev_ath & prev_marketCap
            
            if tokens:
                updates = []
                for token_address, pre_marketCap, prev_ath in tokens:
                    # Single API call for all token data
                    token_data = await get_token_data(token_address)

                    # Ensure token_data is a dictionary before calling .get()
                    if not isinstance(token_data, dict):  
                        logger.error(f"⚠️ Unexpected response type for {token_address}: {type(token_data)} - Value: {token_data}")
                        token_data = {}  # Set to empty dictionary to prevent errors

                    new_marketCap = token_data.get("marketCap", 0)
                    new_volume = token_data.get("volume", 0)
                    new_liquidity = token_data.get("liquidity", 0)

                    if new_marketCap != "Not Available":
                        new_marketCap = float(new_marketCap)

                    # Ignore tokens below 30K
                    if new_marketCap < 30000:
                        
                        await asyncio.sleep(25)
                        continue  # Skip tracking this token

                        #logger.info(f"💰 {token_address} - MarketCap: ${format_number(marketCap)}, Volume: {format_number(volume)}")
                        # await market_to_db(token_address, marketCap, volume)

                        # ✅ Ensure ATH updates correctly
                    new_ath = max(prev_ath or 0, new_marketCap)

                        # ✅ Classify token
                    degen = new_marketCap if new_marketCap >= 100000 else 0

                      
                        # ✅ Update `pot_token` if marketCap is between 55K and 70K
                    pot_token = new_marketCap if 55000 <= new_marketCap <= 70000 else "NO"
                        
                    liquidity_status = new_liquidity if new_liquidity >= 20000 else "NO"
                      # ✅ Set trade condition
                    trade = "BUY" if 58000 <= new_marketCap <= 70000 and liquidity_status != "NO" else "HOLD"

                    logger.info(f"💰 {token_address} - MarketCap: ${format_number(new_marketCap)}, Volume: {format_number(new_volume)}")
                       
                    # Update database
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

                    # Handle graduating tokens
                    if new_marketCap >= 62000:
                        logger.info(f"🎓 {token_address} crossed 60K! Updating status in tokens.db")
                        status = "graduating"
                        #await move_to_graduating_db(token_address, new_marketCap)
                    #else:
                    #    status = "NO"
                    # 🔥 Apply Degen Classification
                        degen_category = await classify_degen(token_address)
                        logger.info(f"🛠️ {token_address} classified as: {degen_category}")
                
                    if new_liquidity < 10_000:
                        print(f"⚠️ Low Liquidity: ${format_number(new_liquidity)}")
                    else:
                        print(f"✅ Total Liquidity: ${format_number(new_liquidity)}")
                
                    if new_marketCap < 20000:
                        logger.warning(f"⚠️{token_address}dropped to 20K! Removing in database.")
                        status = "Inactive"
                        #await delete_tracked_token(token_address)
                        
                    # await asyncio.sleep(40)  # Check every 40 seconds
                    
                if updates:
                    try:
                        await batch_update_tokens(updates)
                        logger.info(f"✅ Successfully updated {len(updates)} tokens.")
                    except Exception as e:
                        logger.error(f"❌ Failed to update tokens update batch: {e}")    
              
            await asyncio.sleep(20)

        except Exception as e:
            logger.error(f"❌ Error in track_graduating_tokens: {e}")
            await asyncio.sleep(10)  # Retry after 10s

async def track_multiple_tokens():
    """Continuously fetch market data for newly added tokens."""
    tracked_tasks = {}

    while True:
        tokens_data = await get_all_tokens()  # ✅ Await the async function
        tokens = set(token["token_address"] for token in tokens_data)  # ✅ Extract token addresses

        logger.info(f"🔍 Found {len(tokens)} tokens in database. Tracking {len(tracked_tasks)} active tasks.")

        # ✅ Stop tracking removed tokens
        for token_address in list(tracked_tasks.keys()):
            if token_address not in tokens:
                tracked_tasks[token_address].cancel()
                del tracked_tasks[token_address]
                logger.info(f"🛑 Stopped tracking {token_address}")

        # ✅ Start tracking new tokens
        for token_address in tokens:
            if token_address not in tracked_tasks:
                logger.info(f"🚀 Starting to track {token_address}")
                tracked_tasks[token_address] = asyncio.create_task(track_market())

        await asyncio.sleep(40)  # ✅ Refresh token list every 40 seconds

async def classify_all_tokens():
    """Fetch token data and classify each token"""
    tokens = await get_all_tokens()  # ✅ Await the async function

    for token in tokens:
        token_address = token["token_address"]
        degen_category = classify_degen(token_address)  # Call the classification function
        logger.info(f"Token: {token_address}, Category: {degen_category}")  # Log instead of print