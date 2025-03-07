import sqlite3
from core.db import TRADE

def update_trailing_stop_loss(token_address, current_price):
    conn = sqlite3.connect(TRADE)
    cursor = conn.cursor()

    cursor.execute("SELECT stop_loss_price FROM bought_tokens WHERE token_address=?", (token_address,))
    row = cursor.fetchone()

    if row and row[0] is not None:
        stop_loss_price = row[0]

        # Move stop-loss up if the price increases
        if current_price > stop_loss_price:
            new_stop_loss = current_price * 0.85  # Example: Stop-loss at 15% below highest price
            cursor.execute("UPDATE bought_tokens SET stop_loss_price=? WHERE token_address=?", (new_stop_loss, token_address))
            conn.commit()
            print(f"🔄 Updated Stop-Loss for {token_address}: {new_stop_loss}")

    else:
        # Set initial stop-loss price
        new_stop_loss = current_price * 0.85
        cursor.execute("UPDATE bought_tokens SET stop_loss_price=? WHERE token_address=?", (new_stop_loss, token_address))
        conn.commit()
        print(f"🚀 Set Initial Stop-Loss for {token_address}: {new_stop_loss}")

    conn.close()
