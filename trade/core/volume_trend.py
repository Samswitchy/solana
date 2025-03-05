import asyncio
from core.market_data import get_trending_data  # ✅ Import data fetch function

async def get_volume_trend(token_address):
    """Improved volume trend analysis with proper number extraction."""
    token_data = await get_trending_data(token_address)

    if not token_data or "pairs" not in token_data:
        return {}

    trends = {}

    for pair in token_data["pairs"]:
        address = pair["baseToken"]["address"]

        def safe_float(value, default=0):
            """Extracts a float safely from a possible nested dictionary."""
            if isinstance(value, dict):  # Check if the value is a dict
                return float(value.get("value", default))  # Extract the numeric value
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        # ✅ Use safe_float to prevent errors
        volume_m5 = safe_float(pair["volume"].get("m5", 0))   
        volume_h1 = safe_float(pair["volume"].get("h1", 0))   
        volume_h6 = safe_float(pair["volume"].get("h6", 0))   
        volume_h24 = safe_float(pair["volume"].get("h24", 0)) 

        price_change_m5 = safe_float(pair["priceChange"].get("m5", 0))   
        price_change_h1 = safe_float(pair["priceChange"].get("h1", 0))   
        price_change_h6 = safe_float(pair["priceChange"].get("h6", 0))   
        price_change_h24 = safe_float(pair["priceChange"].get("h24", 0)) 

        buy_vol = safe_float(pair.get("buyVolume", 0))
        sell_vol = safe_float(pair.get("sellVolume", 0))

        liquidity = safe_float(pair.get("liquidity", 0))
        market_cap = safe_float(pair.get("marketCap", 0))
        fdv = safe_float(pair.get("fdv", 0))

        # 🚨 Check for NaN or invalid values
        if any(v != v for v in [volume_m5, volume_h1, volume_h6, volume_h24]):  # NaN check
            print(f"⚠️ Warning: NaN detected in volume data for {token_address}")
            continue

        # Trend detection logic (adjust as needed)
        if price_change_h1 < -20 and sell_vol > buy_vol * 2:
            trend = "Dumping 🚨"
        elif price_change_m5 > 15 and volume_m5 > volume_h1 * 0.3:
            trend = "Pump Alert 🚀"
        elif price_change_h1 > 20 and price_change_h6 > 50:
            trend = "Uptrend ✅"
        elif sell_vol > buy_vol * 1.5:
            trend = "Selling Pressure 📉"
        elif liquidity < 40000 or market_cap > 100000:
            trend = "High Risk ⚠️"
        else:
            trend = "Stable"

        trends[address] = {
            "volume_m5": volume_m5,
            "volume_h1": volume_h1,
            "volume_h6": volume_h6,
            "volume_h24": volume_h24,
            "price_change_m5": price_change_m5,
            "price_change_h1": price_change_h1,
            "price_change_h6": price_change_h6,
            "price_change_h24": price_change_h24,
            "buy_vol": buy_vol,
            "sell_vol": sell_vol,
            "liquidity": liquidity,
            "market_cap": market_cap,
            "fdv": fdv,
            "trend": trend,
        }

    return trends
