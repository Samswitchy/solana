import asyncio
import datetime
import logging
from modules.database import get_all_tokens, market_to_db, get_market_caps_from_db
from modules.market_data import get_token_data


def calculate_x_gain(old_price, new_price):
    """Calculate how many X the price has increased."""
    if old_price == 0 or old_price is None or new_price is None:  # Prevent division by zero or None values
        return None
    x_gain = new_price / old_price
    return round(x_gain, 2)  # Round to 2 decimal places
 
def fetch_market_caps():
    tokens = get_all_tokens()

    for token in tokens:
        old_price, new_price, timestamp = get_market_caps_from_db(token)  # Fetch values and time

        if old_price and new_price:
            result = calculate_x_gain(old_price, new_price)

            if result and result > 1.5:  # ✅ Only print if X gain is above 1.5X
                #time_achieved = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                time_achieved = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
                time_diff = datetime.datetime.utcnow() - time_achieved

                # Format time difference
                minutes = time_diff.total_seconds() // 60
                hours = int(minutes // 60)
                minutes = int(minutes % 60)
                time_str = f"{hours}h:{minutes}m" if hours else f"{minutes} minutes"

                print(f"🎉 {result}X | 💹 From {old_price}K ↗️ {new_price}K within {time_str}")
            else:
                print(f"🚫 Skipping {token}: Gain is {result}X (less than 1.5X)")
        else:
            print(f"⚠️ Skipping {token}: Missing market cap data.")
fetch_market_caps()
