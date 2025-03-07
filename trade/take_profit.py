import sqlite3
from asell import sell_token
from core.db import TRADE

def check_take_profit_and_sell(token_address, current_price):
    conn = sqlite3.connect(TRADE)
    cursor = conn.cursor()

    cursor.execute("SELECT amount, market_price, tokens_sold FROM bought_tokens WHERE token_address=?", (token_address,))
    row = cursor.fetchone()

    if row:
        total_tokens, buy_price, tokens_sold = row
        x_made = current_price / buy_price  # Calculate profit multiplier

        # Determine how much to sell based on multiplier
        sell_amount = 0
        if x_made >= 3 and tokens_sold == 0:
            sell_amount = total_tokens * 0.50  # Sell 50% at 3x
        elif x_made >= 5 and tokens_sold < 0.75 * total_tokens:
            sell_amount = total_tokens * 0.25  # Sell additional 25% at 5x
        elif x_made >= 10 and tokens_sold < 1.0 * total_tokens:
            sell_amount = total_tokens * 0.25  # Sell remaining 25% at 10x

        if sell_amount > 0:
            print(f"💰 Selling {sell_amount} tokens of {token_address} at {x_made}x")
            txid, received = sell_token(token_address, "So11111111111111111111111111111111111111112", sell_amount)

            if txid:
                cursor.execute("UPDATE bought_tokens SET tokens_sold=tokens_sold+? WHERE token_address=?", (sell_amount, token_address))
                conn.commit()
                print(f"✅ Sold {sell_amount} tokens, updated database.")

    conn.close()
