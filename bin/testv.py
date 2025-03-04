import requests

def get_true_volume(token_address):
    """Fetch and aggregate the 24h trading volume across all DEX pairs for a token."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        total_volume = 0

        if "pairs" in data and isinstance(data["pairs"], list):
            for pair in data["pairs"]:
                volume = pair.get("volume", {}).get("h24", 0)
                liquidity = pair.get("liquidity", {}).get("usd", 0)

                # Ignore pairs with 0 volume or very low liquidity
                if volume > 0 and liquidity > 500:
                    total_volume += volume

        return total_volume if total_volume > 0 else "Low or Manipulated Volume"
    
    return "API Request Failed"

# Example Usage:
token_address = "89S9RdgynPq5odSRmcCDAzg26iYuRw4wqUmzMbjUpump"  # Example token
print(get_true_volume(token_address))
