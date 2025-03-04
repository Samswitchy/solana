import json
import requests
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solders.transaction import Transaction
from solana.rpc.types import TxOpts
from config import HELIUS_RPC_URL, PRIVATE_KEY

def buy_token(input_mint: str, output_mint: str, sol_amount: float = 0.01, priority_fee: float = 0.0007):
    """
    Buy tokens on Solana using Jupiter API.
    :param input_mint: Token mint address of the token being sold (e.g., SOL)
    :param output_mint: Token mint address of the token being bought
    :param sol_amount: Amount of SOL to spend
    :param priority_fee: Priority fee for faster transaction
    """
    client = Client(HELIUS_RPC_URL)
    wallet = Keypair.from_base58_string(PRIVATE_KEY)
    wallet_pubkey = wallet.pubkey()

    # Convert SOL amount to lamports
    amount_lamports = int(sol_amount * 10**9)

    # Get best swap route from Jupiter API
    jupiter_url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_mint}&outputMint={output_mint}&amount={amount_lamports}&slippage=0.5"
    response = requests.get(jupiter_url)
    
    if response.status_code != 200:
        raise Exception("Error fetching quote from Jupiter API")
    
    quote = response.json()

    # Check if 'outputMintDecimals' exists, otherwise set a default value (e.g., 9 decimals)
    decimals = quote.get("outputMintDecimals", 6)  # Default to 9 decimals if missing
    print(decimals)
    # Extract expected output amount
    expected_out_amount = int(quote["outAmount"]) / 10**decimals
    min_received = int(quote["otherAmountThreshold"]) / 10**decimals

    print(f"🔹 Expected to receive: {expected_out_amount} tokens")
    print(f"🔹 Minimum guaranteed after slippage: {min_received} tokens")

    # Prepare transaction
    swap_tx = quote["swapTransaction"]
    transaction = Transaction.deserialize(bytes.fromhex(swap_tx))
    transaction.sign(wallet)

    # Send transaction
    txid = client.send_transaction(transaction, wallet, opts=TxOpts(skip_confirmation=False))

    return txid, expected_out_amount
