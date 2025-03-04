import json
import requests 
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.transaction import Transaction
from solana.rpc.types import TxOpts
from config import HELIUS_RPC_URL, PRIVATE_KEY
from db import get_token_balance

def sell_token(input_mint: str, output_mint: str = "So11111111111111111111111111111111111111112", sell_amount: float = None):
    """
    Sell tokens on Solana using Jupiter API with improved error handling.
    """
    client = Client(HELIUS_RPC_URL)
    wallet = Keypair.from_base58_string(PRIVATE_KEY)
    wallet_pubkey = wallet.pubkey()

    # Fetch token balance
    token_balance = get_token_balance(str(wallet_pubkey), input_mint)
    if token_balance is None:
        print("❌ Could not retrieve token balance.")
        return None, None

    print(f"💰 Wallet Token Balance: {token_balance}")

    # Determine how much to sell
    if sell_amount is None:
        sell_amount = token_balance  # Default: sell full balance

    if sell_amount > token_balance:
        print("❌ Error: Insufficient token balance.")
        return None, None

    # Convert token amount to smallest unit
    amount_in_smallest_unit = int(sell_amount * 10**6)  # Assuming 6 decimals, adjust as needed

    # Get best swap route from Jupiter API
    jupiter_url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_mint}&outputMint={output_mint}&amount={amount_in_smallest_unit}&slippage=0.5"
    response = requests.get(jupiter_url)

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code} - {response.text}")
        return None, None

    quote = response.json()

    # Handle potential errors from API response
    if "error" in quote:
        error_message = quote["error"].lower()
        if "insufficient liquidity" in error_message:
            print("❌ Error: Insufficient liquidity for this trade.")
        elif "small input amount" in error_message:
            print("❌ Error: Input amount is too small. Increase trade size.")
        elif "invalid token mint" in error_message:
            print("❌ Error: Invalid token mint address.")
        elif "rate limit" in error_message:
            print("❌ Error: API rate limit exceeded.")
        else:
            print(f"❌ Unknown error: {error_message}")
        return None, None  

    # Extract expected SOL output amount
    expected_sol = int(quote["outAmount"]) / 10**9  # Convert lamports to SOL
    print(f"🔹 Expected to receive: {expected_sol} SOL")

    # Prepare transaction
    if "swapTransaction" not in quote:
        print("❌ Error: No swapTransaction found in API response.")
        return None, None

    swap_tx = quote["swapTransaction"]
    transaction = Transaction.deserialize(bytes.fromhex(swap_tx))
    transaction.sign(wallet)

    # Send transaction
    try:
        txid = client.send_transaction(transaction, wallet, opts=TxOpts(skip_confirmation=False))
        return txid, expected_sol
    except Exception as e:
        print(f"❌ Transaction Failed: {str(e)}")
        return None, None
