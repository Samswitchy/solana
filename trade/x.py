import asyncio
import datetime
import aiosqlite
import asyncio
import logging
from trade.core.db import get_market_caps_from_db, get_all_tokens
from marketcap import get_token_data

def calculate_x_gain(old_price, new_price):
    """Calculate how many X the price has increased."""
    if old_price == 0 or old_price is None or new_price is None:  # Prevent division by zero or None values
        return None
    x_gain = new_price / old_price
    return round(x_gain, 2)  # Round to 2 decimal places

async def fetch_market_caps():
    tokens = await get_all_tokens()  # ✅ Retrieve all tokens

    for token in tokens:
        token_address = token["token_address"]  # ✅ Extract token address

        old_price, new_price, bought_at, updated_at = get_market_caps_from_db(token_address)

        if old_price and new_price:
            result = calculate_x_gain(old_price, new_price)

            if result and result > 1.5:  
                bought_at = datetime.datetime.strptime(bought_at, "%Y-%m-%d %H:%M:%S")
                updated_time = datetime.datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%f")

                time_diff = updated_time - bought_at  
                minutes = time_diff.total_seconds() // 60
                hours = int(minutes // 60)
                minutes = int(minutes % 60)
                time_str = f"{hours}h:{minutes}m" if hours else f"{minutes} minutes"

                print(f"🌕 Gains {token_address}: Gain is {result}X")
                print(f"🎉 {result}X | 💹 From {old_price}K ↗️ {new_price}K within {time_str}")
            else:
                print(f"🚫 Skipping {token_address}: Gain is {result}X (less than 1.5X)")
        else:
            print(f"⚠️ Skipping {token_address}: Missing market cap data.")

# ✅ Properly run the async function
asyncio.run(fetch_market_caps())
 