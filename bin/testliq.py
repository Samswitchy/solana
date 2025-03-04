import requests
import logging

logger = logging.getLogger(__name__)

def get_liquidity_data(token_address):
    """Fetch total liquidity across all DEX pairs for a given token."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # Mimic browser request
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # Raise an error for bad responses
        
        data = response.json()
        total_liquidity = 0

        if "pairs" in data and isinstance(data["pairs"], list):
            for pair in data["pairs"]:
                liquidity = float(pair.get("liquidity", {}).get("usd", 0))  # Liquidity in USD
                
                # Ignore pairs with very low liquidity
                if liquidity > 10000:
                    total_liquidity += liquidity

        return total_liquidity if total_liquidity > 0 else 0

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch liquidity data for {token_address}: {e}")
        return 0  # Return 0 on failure

# Example usage
token_address = "6Tjd6jYzAWpTPxDZLnWgAy48ovaUios4299HQAkLpump"
liquidity = get_liquidity_data(token_address)
print(f"✅ Total Liquidity: ${liquidity}")
