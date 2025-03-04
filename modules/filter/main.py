# main.py
"""
from modules.trending import calculate_trending_score
from modules.whale_detector import detect_whale_buys
from modules.dex_api import get_dexscreener_data
"""
from trending import calculate_trending_score
from whale_detector import detect_whale_buys
from dex_api import get_dexscreener_data
TOKEN_ADDRESS = "AxriehR6Xw3adzHopnvMn7GcpRFcD41ddpiTWMg6pump"

# Fetch token data
token_data = get_dexscreener_data(TOKEN_ADDRESS)

if token_data:
    score = calculate_trending_score(token_data)
    print(f"Trending Score: {score}/100")

    whales = detect_whale_buys(TOKEN_ADDRESS)
    if whales:
        for whale in whales:
            print(f"🐋 Whale Buy Detected: {whale['amount']} SOL on {TOKEN_ADDRESS}")
