import json
import requests
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.transaction import Transaction
from solana.rpc.types import TxOpts

from solders.compute_budget import set_compute_unit_price
from core.config import HELIUS_RPC_URL, PRIVATE_KEY
from solders.compute_budget import set_compute_unit_price


def sell_token(input_mint: str, sol_amount: float = 0.01, priority_fee: float = 0.0007):
    """
    Sell tokens on Solana using Jupiter API.
    :param input_mint: Token mint address of the token being sold
    :param sol_amount: Amount of token to sell (in token units)
    :param priority_fee: Priority fee for faster transaction
    """
    client = Client(HELIUS_RPC_URL)
    wallet = Keypair.from_base58_string(PRIVATE_KEY)

    # Convert token amount to its smallest unit (lamports equivalent)
    amount_lamports = int(sol_amount * 10**9)  # Adjust decimals if needed

    # Get best swap route from Jupiter API (Selling token for SOL)
    jupiter_url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_mint}&outputMint=So11111111111111111111111111111111111111112&amount={amount_lamports}&slippage=0.5"
    response = requests.get(jupiter_url)

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code} - {response.text}")
        return None, None

    quote = response.json()

    # Handle errors in API response
    if "error" in quote:
        error_message = quote["error"].lower()
        if "insufficient liquidity" in error_message:
            print("❌ Error: Insufficient liquidity for this trade.")
        elif "small input amount" in error_message:
            print("❌ Error: Input amount is too small. Increase trade size.")
        elif "invalid token mint" in error_message:
            print("❌ Error: Invalid token mint address.")
        elif "rate limit" in error_message:
            print("❌ Error: API rate limit exceeded. Try again later.")
        else:
            print(f"❌ Unknown error: {error_message}")
        return None, None

    # Extract expected output amount
    decimals = quote.get("outputMintDecimals", 6)  # SOL usually has 9 decimals
    expected_sol = int(quote["outAmount"]) / 10**decimals

    print(f"🔹 Expected to receive: {expected_sol} SOL")

    # Prepare transaction
    # Prepare transaction
    if "swapTransaction" not in quote:
        print("❌ Error: No swapTransaction found in API response.")
        return None, None

    swap_tx = quote["swapTransaction"]
    transaction = Transaction.deserialize(bytes.fromhex(swap_tx))

    # ✅ Apply priority fee (convert SOL to lamports)
    priority_lamports = int(priority_fee * 10**9)
    transaction.add(set_compute_unit_price(priority_lamports))  # Add fee adjustment

    # ✅ Sign and send transaction
    transaction.sign(wallet)

    # Send transaction
    try:
        txid = client.send_transaction(transaction, wallet, opts=TxOpts(skip_confirmation=False))
        return txid, expected_sol
    except Exception as e:
        print(f"❌ Transaction Failed: {str(e)}")
        return None, None
