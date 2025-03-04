# modules/whale_detector.py
from dex_api import get_dexscreener_transactions

def detect_whale_buys(token_address, min_buy_amount=5):
    """Monitors Dexscreener for large whale buys."""
    txs = get_dexscreener_transactions(token_address)
    whale_buys = []

    for tx in txs:
        if tx["amount"] >= min_buy_amount:
            whale_buys.append(tx)

    return whale_buys
