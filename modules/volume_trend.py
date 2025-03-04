import asyncio
from modules.market_data import get_trending_data  # ✅ Import data fetch function

async def get_volume_trend(token_address):
    """Analyze volume trend over multiple timeframes."""
    token_data = await get_trending_data(token_address)

    if not token_data or "pairs" not in token_data:
        return {}

    trends = {}

    for pair in token_data["pairs"]:
        address = pair["baseToken"]["address"]
        volume_m5 = pair["volume"].get("m5", 0)   # Last 5 minutes
        volume_h1 = pair["volume"].get("h1", 0)   # Last 1 hour
        volume_h6 = pair["volume"].get("h6", 0)   # Last 6 hours
        volume_h24 = pair["volume"].get("h24", 0) # Last 24 hours

        # Compare volume changes over time
        trend = "Stable"
        if volume_m5 > volume_h1 * 0.3:  # If 5-min volume is 30% of 1-hour volume
            trend = "Surging 📈"
        elif volume_h1 > volume_h6 * 0.5:  # If 1-hour volume is 50% of 6-hour volume
            trend = "Increasing 🔥"
        elif volume_h6 > volume_h24 * 0.5:  # If 6-hour volume is 50% of 24-hour volume
            trend = "Uptrend ✅"
        elif volume_m5 < volume_h1 * 0.1:  # If 5-min volume is very low
            trend = "Dropping 📉"

        trends[address] = {
            "m5": volume_m5,
            "h1": volume_h1,
            "h6": volume_h6,
            "h24": volume_h24,
            "trend": trend,
        }

    return trends
