#from modules.db import get_mint_address, save_bought_token
from trade.core.db import get_mint_address, save_bought_token
from marketcap import get_token_marketcap
from abuy import buy_token

SOL_MINT = "So11111111111111111111111111111111111111112"

# Get token mint address from database
TOKEN_MINT = get_mint_address()
print(TOKEN_MINT)

if TOKEN_MINT:
    txid, expected_tokens = buy_token(SOL_MINT, TOKEN_MINT, sol_amount=0.01, priority_fee=0.0007)

    if txid and expected_tokens is not None:
        print(f"✅ Swap successful! Tx ID: {txid}")
        print(f"🔹 You received ~{expected_tokens} tokens")

        # Fetch price & market cap
        price, market_cap = get_token_marketcap(TOKEN_MINT)

        # Save token details
        save_bought_token(TOKEN_MINT, expected_tokens, txid, price, market_cap)
    else:
        print("❌ Swap failed.")
else:
    print("❌ No token mint address found in the database.")
