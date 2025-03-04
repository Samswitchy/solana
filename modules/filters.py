import logging
from modules.market_data import get_token_data, get_volume_data  # ✅ Correct import path

logger = logging.getLogger(__name__)

async def classify_degen(token_address):
    """
    Classify a token into Low-Degen, Mid-Degen, or High-Degen based on market cap and volume.
    """
    try:
        # Fetch real-time market data asynchronously
        marketCap = float(await get_token_data(token_address) or 0)  # ✅ Await async function
        volume = float(await get_volume_data(token_address) or 0)  # ✅ Await async function

        # Classification rules
        if marketCap < 50000 or volume < 10000:
            return "Not Degen"

        if 50000 <= marketCap < 110000 and volume >= 15000:
            return "Low-Degen"

        if 150000 <= marketCap <= 550000 and volume >= 500000:
            return "Mid-Degen"

        if marketCap > 550000 and volume >= 100000:
            return "High-Degen"

        return "Unknown"

    except Exception as e:
        logger.error(f"Error classifying {token_address}: {e}")
        return "Invalid Data"
