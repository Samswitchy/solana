import time
import traceback
from db import fetch_info, save_bought_token, fetch_bought_tokens
from marketcap import get_token_marketcap
from abuy import buy_token
 
SOL_MINT = "So11111111111111111111111111111111111111112"
COOLDOWN_PERIOD = 3600  # 1 hour cooldown before rebuying the same token

def buy_tokens_if_needed():
    """Checks tokens in DB and buys if trade = 'BUY'."""
    print("\n🔄 Checking tokens for buying opportunities...")

    tokens = fetch_info()  # ✅ Fetch tokens marked as "BUY"
    bought_tokens = {token[0] for token in fetch_bought_tokens()}  # ✅ Get already bought token addresses

    if not tokens:
        print("❌ No valid tokens found in the database.")
    else:
        current_time = time.time()
        
        for TOKEN_MINT, POT_TOKEN, DB_MARKETCAP, TRADE in tokens:
            if TOKEN_MINT in bought_tokens:  # ✅ Skip if already bought
                print(f"🚫 Skipping {TOKEN_MINT}, already bought before.")
                continue

            print(f"🔍 Checking Token: {TOKEN_MINT}, Pot_token: {POT_TOKEN}, Stored MarketCap: {DB_MARKETCAP}, Trade: {TRADE}")

            if TRADE == "BUY":
                price, market_cap = get_token_marketcap(TOKEN_MINT)
                print(f"🔹 Live MarketCap: {market_cap}")

                if 58000 <= market_cap <= 70000:
                    print(f"✅ Conditions met! Buying token: {TOKEN_MINT}")

                    txid, expected_tokens = buy_token(SOL_MINT, TOKEN_MINT, sol_amount=0.01, priority_fee=0.0005)

                    if txid and expected_tokens is not None:
                        print(f"✅ Swap successful! Tx ID: {txid}")
                        print(f"🔹 You received ~{expected_tokens} tokens")

                        save_bought_token(TOKEN_MINT, expected_tokens, txid, price, market_cap)
                        break  # ✅ Stop checking once a token is bought
                    else:
                        print("❌ Swap failed.")
                else:
                    print(f"🚫 Market conditions not met for {TOKEN_MINT}.")
            else:
                print(f"🚫 Skipping {TOKEN_MINT}, trade is not 'BUY'.")

    print("✅ Done checking all tokens.\n")


# ✅ Run in an infinite loop every 5 seconds with error handling
if __name__ == "__main__":
    while True:
        try:
            buy_tokens_if_needed()
        except Exception as e:
            print(f"⚠️ Critical Error: {e}. Retrying in 10 seconds...")
            traceback.print_exc()  # 🔹 Log the full error
            time.sleep(10)  # ✅ Give it some time before retrying

        print("⏳ Waiting for 5 seconds before next check...\n")
        time.sleep(5)