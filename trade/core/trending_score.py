import sys
import os
from collections import defaultdict

from core.market_data import get_trending_data  # ✅ Updated import

async def calculate_trending_score(token_address):
    """Calculate trending score based on token data."""
    token_data = await get_trending_data(token_address)

    if not token_data or "pairs" not in token_data:
        return {}

    scores = defaultdict(lambda: {
        "volume": 0, "buys": 0, "sells": 0, "price_change": 0,
        "liquidity": 0, "boost": 0
    })

    for pair in token_data["pairs"]:
        liquidity = pair.get("liquidity", {}).get("usd", 0)

        # ✅ Only process pairs with liquidity > 0
        if liquidity > 5000:
            address = pair["baseToken"]["address"]

            # ✅ Extract price changes from multiple timeframes
            price_changes = pair.get("priceChange", {})
            price_m5 = price_changes.get("m5", 0)   # Last 5 minutes
            price_h1 = price_changes.get("h1", 0)   # Last 1 hour
            price_h6 = price_changes.get("h6", 0)   # Last 6 hours

            # ✅ Apply a weighted formula for short-term impact
            weighted_price_change = (
                (price_m5 * 0.4) +   # 40% weight for 5 min change
                (price_h1 * 0.35) +  # 35% weight for 1 hour change
                (price_h6 * 0.25)    # 25% weight for 6 hour change
            )

            # 📌 Print each token's trading data
            print(f"\n📌 Token: {address}")
            print(f"   - Volume: {pair['volume'].get('h24', 0)}")
            print(f"   - Buys: {pair['txns'].get('h24', {}).get('buys', 0)}")
            print(f"   - Sells: {pair['txns'].get('h24', {}).get('sells', 0)}")
            print(f"   - Weighted Price Change: {weighted_price_change:.2f}%")
            print(f"   - Liquidity: ${liquidity}")
            print(f"   - Boost: {pair.get('boosts', {}).get('active', 0)}")

            scores[address]["volume"] += pair["volume"].get("h24", 0)
            scores[address]["buys"] += pair["txns"].get("h24", {}).get("buys", 0)
            scores[address]["sells"] += pair["txns"].get("h24", {}).get("sells", 0)
            scores[address]["price_change"] += weighted_price_change  # ✅ Use weighted price change
            scores[address]["liquidity"] += liquidity
            scores[address]["boost"] += pair.get("boosts", {}).get("active", 0)

    final_scores = {}
    for address, data in scores.items():
        buy_sell_ratio = (data["buys"] + 1) / (data["sells"] + 1)
        trending_score = (
            (data["volume"] / 1000) * 0.3 +
            (buy_sell_ratio * 20) * 0.25 +
            (data["price_change"] * 0.2) +  # ✅ Weighted price change now used
            (data["liquidity"] / 1000) * 0.15 +
            (data["boost"] * 10) * 0.1
        )

        final_scores[address] = trending_score

    return sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
