import requests
import logging

logger = logging.getLogger(__name__)

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens/"

def get_token_price(token_address):
    """Fetches the latest price of a token using Dexscreener API."""
    try:
        url = f"{DEXSCREENER_API}{token_address}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if "pairs" in data and data["pairs"]:
                pair = data["pairs"][0]  # Take the first available pair
                price = pair.get("priceUsd", "Not Available")
                return price
        return "Not Available"
    
    except Exception as e:
        logger.error(f"❌ Error fetching price: {e}")
        return "API Error"
