import requests

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
WHALE_THRESHOLD_SOL = 0.01  # Define your whale buy threshold

def get_recent_transactions(pool_address):
    """Fetches recent transactions for a given liquidity pool address"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [pool_address, {"limit": 10}]
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    return response.get("result", [])

def get_transaction_details(signature):
    """Fetches transaction details for a given signature"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",  # Correct method
        "params": [signature, "json"]
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    return response.get("result", {})

def detect_whale_buys(pool_address):
    transactions = get_recent_transactions(pool_address)
    
    if not transactions:
        print("No transactions found for this pool.")
        return

    print(f"Fetched {len(transactions)} transactions.")
    
    for txn in transactions:
        signature = txn.get('signature')
        print(f"Fetching details for Tx: {signature}")  # Debug print
        details = get_transaction_details(signature)

        if not details:
            print(f"Skipping {signature} (No details found, might not be finalized yet).")
            continue


        print(f"Processing Tx: {signature}")

        # Check SOL balance changes
        pre_balances = details.get("meta", {}).get("preBalances", [])
        post_balances = details.get("meta", {}).get("postBalances", [])

        if pre_balances and post_balances and len(pre_balances) == len(post_balances):
            for i in range(len(pre_balances)):
                sol_change = (post_balances[i] - pre_balances[i]) / 1e9  # Convert lamports to SOL
                if sol_change >= WHALE_THRESHOLD_SOL:
                    print(f"🚨 Whale Buy Detected! {sol_change} SOL in Tx: {signature}")

# Example usage (Replace with actual liquidity pool address)
detect_whale_buys("4ELGifwr2jHtEaFZUXXvQLAYiE6W5bvpWYZbJTRSpump")
