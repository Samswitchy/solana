import json
import requests
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.transaction import Transaction
from solana.rpc.types import TxOpts
from core.config import HELIUS_RPC_URL, PRIVATE_KEY

def buy_token(input_mint: str, output_mint: str, sol_amount: float = 0.01, priority_fee: float = 0.0007):
    """
    Buy tokens on Solana using Jupiter API with improved error handling.
    """
    client = Client(HELIUS_RPC_URL)
    wallet = Keypair.from_base58_string(PRIVATE_KEY)
    
    # Convert SOL amount to lamports
    amount_lamports = int(sol_amount * 10**9)

    # Get best swap route from Jupiter API
    jupiter_url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_mint}&outputMint={output_mint}&amount={amount_lamports}&slippage=0.5"
    response = requests.get(jupiter_url)

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code} - {response.text}")
        return None, None

    quote = response.json()

    # Check if an error is returned in the API response
    if "error" in quote:
        error_message = quote["error"].lower()
        
        if "insufficient liquidity" in error_message:
            print("❌ Error: Insufficient liquidity for this trade.")
        elif "small input amount" in error_message:
            print("❌ Error: Input amount is too small. Increase trade size.")
        elif "invalid token mint" in error_message:
            print("❌ Error: One or both token mint addresses are incorrect.")
        elif "rate limit" in error_message:
            print("❌ Error: API rate limit exceeded. Try again later.")
        else: 
            print(f"❌ Unknown error: {error_message}")

        return None, None  # Exit early if an error is detected

    # Extract expected output amount
    decimals = quote.get("outputMintDecimals", 6)
    expected_out_amount = int(quote["outAmount"]) / 10**decimals

    print(f"🔹 Expected to receive: {expected_out_amount} tokens")

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
        return txid, expected_out_amount
    except Exception as e:
        print(f"❌ Transaction Failed: {str(e)}")
        return None, None
