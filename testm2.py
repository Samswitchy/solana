import asyncio
import logging
from modules.database import get_all_tokens, market_to_db, move_to_graduating_db  # Fetch token addresses
from modules.market_data import get_token_data, get_volume_data, get_liquidity_data  # Fetch market data

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def format_number(num):
    return f"{num:,.2f}" if num is not None else "N/A"

async def track_market(token_address):
    """Fetch MarketCap, volume, and liquidity and update the database continuously."""
    while True:
        try:
            token_data = await get_token_data(token_address)
            marketCap = token_data.get("marketCap", 0)

            volume = await get_volume_data(token_address)
            liquidity = await get_liquidity_data(token_address)
            logger.info(f"🔍 Raw marketCap response for {token_address}: {marketCap}")

            if isinstance(marketCap, str):
                try:
                    marketCap = float(marketCap.replace(",", ""))
                except ValueError:
                    logger.error(f"Invalid marketCap value: {marketCap}")
                    marketCap = None

            if not marketCap or marketCap < 30000:
                logger.warning(f"🚫 Ignoring {token_address} (MarketCap: ${format_number(marketCap)}) - Too Low")
                await asyncio.sleep(40)
                continue  

            logger.info(f"💰 {token_address} - MarketCap: ${format_number(marketCap)}, Volume: {format_number(volume)}")
            await market_to_db(token_address, marketCap, volume)

            if marketCap >= 65000:
                logger.info(f"🎓 {token_address} has crossed 60K! Moving to graduating_db")
                await move_to_graduating_db(token_address, marketCap)

            if liquidity < 10_000:
                logger.warning(f"⚠️ Low Liquidity: ${format_number(liquidity)}")
            else:
                logger.info(f"✅ Total Liquidity: ${format_number(liquidity)}")

        except asyncio.CancelledError:
            logger.info(f"🛑 Task cancelled for {token_address}")
            break
        except Exception as e:
            logger.error(f"❌ Error tracking {token_address}: {e}")

        await asyncio.sleep(40)  # Wait before next update

async def track_all_tokens():
    """Fetch all tokens and start tracking market data for each."""
    tokens = await get_all_tokens()
    
    if not tokens:
        logger.warning("⚠️ No tokens found in the database.")
        return

    tasks = [track_market(token["token_address"]) for token in tokens]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(track_all_tokens())
