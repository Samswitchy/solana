# modules/dex_api.py
import requests

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens"

def get_dexscreener_data(token_address):
    response = requests.get(f"{DEXSCREENER_API}/{token_address}")
    if response.status_code == 200:
        data = response.json()
        if "pairs" in data and data["pairs"]:
            pair_data = data["pairs"][0]  # ✅ Extract first pair
            return {
                "volume": pair_data.get("volume", {}).get("h24", 0),  # ✅ Extract 24-hour volume
                "liquidity": pair_data.get("liquidity", 0),
                "buys": pair_data.get("buys", 0),
                "sells": pair_data.get("sells", 0),
                "holder_growth": 0,  # Placeholder (needs separate API)
                "whale_buys": 0  # Placeholder
            }
    return {"volume": 0, "liquidity": 0, "buys": 0, "sells": 0, "holder_growth": 0, "whale_buys": 0}


def get_dexscreener_transactions(token_address):
    """Fetches recent transactions for a token."""
    data = get_dexscreener_data(token_address)
    if data and "pairs" in data:
        return data["pairs"][0].get("txs", [])  # Extract transactions
    return []
