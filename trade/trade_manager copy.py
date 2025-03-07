import time
from core.db import fetch_bought_tokens, update_token_data
from marketcap import get_token_marketcap
from asell import sell_token

# 🛠 Define stop-loss and take-profit strategy
TAKE_PROFIT_LEVELS = [3, 5, 10]  # Sell portions at 3x, 5x, 10x
STOP_LOSS_PERCENT = 30  # Stop-loss at 30% drop from peak
TRAILING_STOP_LOSS_PERCENT = 20  # Moves up with price

# Default Output Mint (Selling for SOL)
OUTPUT_MINT = "So11111111111111111111111111111111111111112"

# Priority Fee for Faster Transactions
PRIORITY_FEE = 0.0007

def check_take_profit_and_sell(token_mint, bought_price, amount):
    """Sell portions of tokens at profit milestones (3x, 5x, 10x)."""
    current_price, _ = get_token_marketcap(token_mint)

    if not current_price:
        print(f"❌ Error fetching price for {token_mint}")
        return None

    profit_multiplier = current_price / bought_price

    for level in TAKE_PROFIT_LEVELS:
        if profit_multiplier >= level:
            sell_amount = amount * 0.50  # Sell 50% of holdings
            print(f"🚀 Selling {sell_amount} of {token_mint} at {level}x profit!")
            txid, received = sell_token(token_mint, OUTPUT_MINT, sell_amount, PRIORITY_FEE)
            if txid:
                print(f"✅ Sold {sell_amount} of {token_mint} at {level}x - Tx: {txid}")
                update_token_data(token_mint, "x_sold", f"{level}x")
                return txid
    return None

def check_stop_loss_and_sell(token_mint, bought_price, highest_price, amount):
    """Sell token if it drops below trailing stop-loss."""
    current_price, _ = get_token_marketcap(token_mint)

    if not current_price:
        print(f"❌ Error fetching price for {token_mint}")
        return None

    # Update highest price if new peak is reached
    if current_price > highest_price:
        highest_price = current_price
        update_token_data(token_mint, "new_marketcap", highest_price)

    # Calculate trailing stop-loss price
    stop_loss_price = highest_price * (1 - TRAILING_STOP_LOSS_PERCENT / 100)

    # Sell if price drops below stop-loss
    if current_price < stop_loss_price:
        print(f"🚨 Stop-loss triggered for {token_mint}! Selling all tokens.")
        txid, received = sell_token(token_mint, OUTPUT_MINT, sell_amount=amount, priority_fee=PRIORITY_FEE)
        if txid:
            print(f"✅ Sold {amount} of {token_mint} due to stop-loss - Tx: {txid}")
            update_token_data(token_mint, "x_sold", "STOP-LOSS")
        return txid
    return None

def monitor_market():
    """Continuously checks tokens and sells based on conditions."""
    while True:
        tokens = fetch_bought_tokens()
        if not tokens:
            print("⏳ No bought tokens to monitor...")
        else:
            for token in tokens:
                token_mint, amount, _, bought_price, highest_price = token

                # Check take-profit first
                txid = check_take_profit_and_sell(token_mint, bought_price, amount)

                # If not sold at profit, check stop-loss
                if not txid:
                    check_stop_loss_and_sell(token_mint, bought_price, highest_price, amount)

        print("⏳ Waiting before next check...")
        time.sleep(10)  # Adjust based on preference
