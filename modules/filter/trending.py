def calculate_trending_score(data):
    print(f"🔍 DEBUG: Data received → {data}")  # Check structure before using it

    liquidity = data.get("liquidity", 0)
    volume = data.get("volume", 0)
    buys = data.get("buys", 0)
    sells = data.get("sells", 0)
    holder_growth = data.get("holder_growth", 0)
    whale_buys = data.get("whale_buys", 0)

    # Confirm the variable type
    print(f"🔍 DEBUG: Type of volume → {type(volume)}") 

    buy_sell_ratio = (buys + 1) / (sells + 1)

    # **Possible Fix**
    if isinstance(volume, dict):  
        print("⚠️ WARNING: 'volume' is a dictionary! Extracting correct value...")
        volume = volume.get("h24", 0)  # Extract 24-hour volume if it exists

    volume_factor = min(volume / 1000, 10)
    liquidity_factor = min(liquidity / 500, 10)
    holder_factor = min(holder_growth / 50, 10)
    whale_factor = min(whale_buys / 2, 10)

    trending_score = (
        (buy_sell_ratio * 20) +  
        (volume_factor * 20) +
        (liquidity_factor * 15) +
        (holder_factor * 25) +
        (whale_factor * 20)  
    )

    print(f"🔍 DEBUG: buy_sell_ratio={buy_sell_ratio}, volume_factor={volume_factor}, liquidity_factor={liquidity_factor}, holder_factor={holder_factor}, whale_factor={whale_factor}")
    print(f"🔍 DEBUG: Trending Score: {trending_score}")

    return min(trending_score, 100)
