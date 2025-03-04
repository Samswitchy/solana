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
    batch_update_graduating_tokens,
    delete_graduating_token,
)
from modules.market_data import get_token_data, get_volume_data, get_liquidity_data

logger = logging.getLogger(__name__)

from modules.market_data import (
    get_token_data, get_holders_data, 
    get_volume_data ,
    get_holders_data,
 ) # ✅ Import holders & volume functions
#from trade.bmain import buy_tokens_if_needed


async def track_market(token_address):
    """Fetch MarketCap, holders, and volume every 60 seconds and update the database."""
    while True:
        marketCap = await get_token_data(token_address)
        volume = await get_volume_data(token_address)
        liquidity = await get_liquidity_data(token_address)

        if marketCap != "Not Available":
            marketCap = float(marketCap)

           
            # Ignore tokens below 30K
            if marketCap < 30000:
                logger.warning(f"🚫 Ignoring {token_address} (MarketCap: ${format_number(marketCap)}) - Too Low")
                await asyncio.sleep(40)
                continue  # Skip tracking this token

            logger.info(f"💰 {token_address} - MarketCap: ${format_number(marketCap)}, Volume: {format_number(volume)}")
            await market_to_db(token_address, marketCap, volume)


            if marketCap >= 62000:
                logger.info(f"🎓 {token_address} has crossed 60K! Moving to graduating_db")
                await move_to_graduating_db(token_address, marketCap)  # ✅ Move to graduating DB
                # 🔥 Apply Degen Classification
                degen_category = await classify_degen(token_address)
                logger.info(f"🛠️ {token_address} classified as: {degen_category}")  # ✅ Log classification
            if liquidity < 10_000:
                print(f"⚠️ Low Liquidity: ${format_number(liquidity)}")
            else:
                print(f"✅ Total Liquidity: ${format_number(liquidity)}")
        await asyncio.sleep(40)  # Check every 40 seconds


import asyncio
import logging

logger = logging.getLogger(__name__)

async def track_graduating_tokens():
    """Track tokens already in graduating.db and update their market cap."""
    while True:
        try:
            tokens = await fetch_graduating_tokens()  # ✅ Use async function

            if tokens:
                updates = []
                for token_address, prev_marketCap, prev_ath in tokens:
                    new_marketCap = await get_token_data(token_address)
                    new_volume = await get_volume_data(token_address)
                    new_liquidity = await get_liquidity_data(token_address)

                    if new_marketCap != "Not Available":
                        new_marketCap = float(new_marketCap)

                        # ✅ Classify degen level
                        degen_classification = await classify_degen(token_address)

                        # ✅ Store marketCap in 'degen' column if ≥ 100K
                        degen = new_marketCap if new_marketCap >= 100000 else 0
                        
                        #ath = new_marketCap


                          # ✅ Update ATH (All-Time High) only if new_marketCap is greater
                        new_ath = max(prev_ath, new_marketCap) if prev_ath else new_marketCap

                        # ✅ Conditions for pot_token, liquidity, and trade
                        pot_token = 61000 if new_marketCap >= 61000 else "NO"
                        liquidity = new_liquidity if new_liquidity >= 20000 else "NO"
                        trade = "BUY" if 58000 <= new_marketCap <= 70000 and liquidity != "NO" else "HOLD"

                        if new_marketCap > prev_marketCap:
                            #updates.append((new_marketCap, new_volume, pot_token, liquidity, degen, trade, token_address))
                            updates.append((
                            new_marketCap,  # ✅ marketCap
                            new_volume,     # ✅ volume
                            pot_token,      # ✅ pot_token
                            liquidity,      # ✅ liquidity
                            trade,          # ✅ trade (before degen)
                            degen,          # ✅ degen (last before token_address)
                            new_ath, 
                            token_address   # ✅ token_address (WHERE condition)
                        ))


                            

                        elif new_marketCap < 55000:  # Remove if below 58K
                            logger.warning(f"⚠️ {token_address} dropped below 58K! Removing from graduating_db.")
                            delete_graduating_token(token_address)

                if updates:
                    try:
                        await batch_update_graduating_tokens(updates)  # ✅ Properly await async function

                        logger.info(f"✅ Successfully updated {len(updates)} graduating tokens.")
                    except Exception as e:
                        logger.error(f"❌ Failed to update graduating tokens: {e}")

            await asyncio.sleep(30)  # ✅ Check every 30 seconds

        except Exception as e:
            logger.error(f"❌ Error in track_graduating_tokens: {e}")
            await asyncio.sleep(10)  # Wait 10s before retrying in case of failure


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

        await asyncio.sleep(80)  # ✅ Refresh token list every 80 seconds

async def classify_all_tokens():
    """Fetch token data and classify each token"""
    tokens = await get_all_tokens()  # ✅ Await the async function

    for token in tokens:
        token_address = token["token_address"]
        degen_category = classify_degen(token_address)  # Call the classification function
        logger.info(f"Token: {token_address}, Category: {degen_category}")  # Log instead of print
