from modules.wash_trading import (
    detect_wash_trading,
    detect_high_frequency_trading,
    detect_circular_trading,
    detect_volume_without_price_change
)
import requests
import time

DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/tokens/{contract_address}"

def fetch_token_transactions(contract_address):
    """
    Fetches transactions from DexScreener API.
    """
    url = DEXSCREENER_API_URL.format(contract_address=contract_address)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print("🔍 API Response:", data)  # Debugging step

        # Check if the API response contains transactions
        if "pairs" in data and len(data["pairs"]) > 0:
            transactions = data["pairs"][0].get("txns", [])
            print("🔍 Extracted Transactions:", transactions)  # Debugging step
            return transactions
    
    return []  # Return empty list if no transactions found

def analyze_wash_trading(contract_address):
    """
    Fetches transactions, detects wash trading, and logs results.
    """
    transactions = fetch_token_transactions(contract_address)
    
    if not isinstance(transactions, list):
        print(f"⚠️ Unexpected transaction format: {type(transactions)}")
        print(f"Transactions data: {transactions}")  # Debugging output
        return

    if not transactions:
        print(f"⚠️ No transactions found for {contract_address}")
        return

    print("🔍 Sample Transaction:", transactions[0])

    formatted_transactions = []
    for tx in transactions:
        try:
            formatted_transactions.append({
                "wallet": tx.get("from", "Unknown"),
                "amount": float(tx.get("amount", 0)),  # Ensure it's a number
                "type": tx.get("side", "Unknown"),
                "timestamp": int(tx.get("timestamp", 0))  # Ensure it's an integer
            })
        except Exception as e:
            print(f"⚠️ Skipping transaction due to error: {e}")

    if formatted_transactions:
        suspicious_wallets = detect_wash_trading(formatted_transactions)
        suspicious_times = detect_high_frequency_trading(formatted_transactions)
        suspicious_pairs = detect_circular_trading(formatted_transactions)

        print(f"\n🚨 Analyzing {contract_address} 🚨")
        print("Suspicious Wash Trading Wallets:", suspicious_wallets)
        print("Suspicious High-Frequency Trades:", suspicious_times)
        print("Suspicious Circular Trading Pairs:", suspicious_pairs)
    else:
        print("⚠️ No valid transactions to analyze.")


tracked_tokens = ["9QdkYK1H1cCqos2ZKqmmnKfdzaJUvhskEHtkrmo6pump", "AeBDvTBaWFeZa1oA6J4vxMixpCfk8cRgioTo4FZNpump"]

while True:
    for token in tracked_tokens:
        analyze_wash_trading(token)
    
    time.sleep(60)  # Runs every 60 seconds
