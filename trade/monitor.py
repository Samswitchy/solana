import time
#from modules.marketcap import update_marketcap
from marketcap import update_marketcap

"""
while True:
    update_marketcap()
    time.sleep(300)  # Runs every 5 minutes
"""


def monitor_market():
    tokens = fetch_bought_tokens()  # Get all bought tokens

    for token in tokens:
        token_address = token[0]
        current_price, market_cap = get_token_marketcap(token_address)  # Fetch live price

        # ✅ Update Stop-Loss
        update_trailing_stop_loss(token_address, current_price)

        # ✅ Check if Take-Profit Level is Met
        check_take_profit_and_sell(token_address, current_price)

        # ✅ Check if Stop-Loss is Hit
        check_stop_loss_and_sell(token_address, current_price)

if __name__ == "__main__":
    while True:
        try:
            monitor_market()
        except Exception as e:
            print(f"⚠️ Error: {e}, Retrying in 10 seconds...")
            time.sleep(10)

        print("⏳ Waiting for next check...")
        time.sleep(5)  # Check every 5 seconds
