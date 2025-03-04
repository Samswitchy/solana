import time
from db import fetch_info, save_bought_token
from marketcap import get_token_marketcap
from abuy import buy_token

SOL_MINT = "So11111111111111111111111111111111111111112"

def check_and_buy_tokens():
    """Continuously checks tokens and buys if conditions are met."""
    while True:  # ✅ Infinite loop
        print("\n🔄 Checking tokens for buying opportunities...")

        # Fetch all tokens with pot_token and marketcap
        tokens = fetch_info()

        if not tokens:
            print("❌ No valid tokens found in the database.")
        else:
            for TOKEN_MINT, POT_TOKEN, DB_MARKETCAP in tokens:
                print(f"🔍 Checking Token: {TOKEN_MINT}, Pot_token: {POT_TOKEN}, Stored MarketCap: {DB_MARKETCAP}")

                # Fetch current market price & market cap
                price, market_cap = get_token_marketcap(TOKEN_MINT)
                print(f"🔹 Live MarketCap: {market_cap}")

                # Check conditions
                if POT_TOKEN == 82000 and (82000 <= market_cap <= 94000):
                    print(f"✅ Conditions met! Buying token: {TOKEN_MINT}")

                    # Proceed with buy
                    txid, expected_tokens = buy_token(SOL_MINT, TOKEN_MINT, sol_amount=0.01, priority_fee=0.0005)

                    if txid and expected_tokens is not None:
                        print(f"✅ Swap successful! Tx ID: {txid}")
                        print(f"🔹 You received ~{expected_tokens} tokens")

                        # Save token details
                        save_bought_token(TOKEN_MINT, expected_tokens, txid, price, market_cap)
                        break  # ✅ Stop checking once a token is bought
                    else:
                        print("❌ Swap failed.")
                else:
                    print(f"🚫 Market conditions not met: Pot_token = {POT_TOKEN}, MarketCap = {market_cap} (DB: {DB_MARKETCAP})")

            print("✅ Done checking all tokens. Waiting for 10 seconds...\n")

        time.sleep(5)  # ✅ Wait 10 seconds before checking again

# Run the function
check_and_buy_tokens()
