import asyncio
import os, sys
from db import fetch_info  # ✅ Import the acleasync function
# Get the project root directory (two levels up)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add it to sys.path if not already included
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from modules.trending_score import calculate_trending_score  # ✅ Import correctly
from modules.volume_trend import get_volume_trend           # ✅ New volume trend module

async def main():
    # ✅ Fetch token addresses from database
    # tokens = await fetch_info()
    tokens = fetch_info()

    if not tokens:
        print("⚠️ No tokens found in the database.")
        return

    for token_address, pot_token, marketcap, trade in tokens:
        print(f"\n🔹 Processing {token_address}")

        # ✅ Get trending score
        try:
            scores = await calculate_trending_score(token_address)
            print("Trending Score:", scores)
        except Exception as e:
            print(f"❌ Error calculating trending score for {token_address}: {e}")
            continue  # Skip to the next token

        # ✅ Get volume trend
        try:
            volume_trend = await get_volume_trend(token_address)
            print("Volume Trend:", volume_trend)
        except Exception as e:
            print(f"❌ Error getting volume trend for {token_address}: {e}")
            continue  # Skip to the next token

# Run the async function
asyncio.run(main())  # ✅ Correct way to execute async code


