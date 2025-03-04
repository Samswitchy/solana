from collections import defaultdict
import datetime

def detect_wash_trading(transactions):
    """
    Detects wallets that frequently buy and sell the same token, indicating potential wash trading.
    
    :param transactions: List of transaction dictionaries with keys: wallet, amount, type (buy/sell)
    :return: List of suspicious wallets
    """
    wallet_activity = defaultdict(lambda: {"buys": 0, "sells": 0})

    for tx in transactions:
        wallet = tx["wallet"]
        amount = tx["amount"]
        action = tx["type"]  # "buy" or "sell"

        if action == "buy":
            wallet_activity[wallet]["buys"] += amount
        elif action == "sell":
            wallet_activity[wallet]["sells"] += amount

    suspicious_wallets = []
    for wallet, data in wallet_activity.items():
        buy_sell_ratio = data["buys"] / (data["sells"] + 1)  # Avoid division by zero
        if 0.9 <= buy_sell_ratio <= 1.1:  # Buying and selling similar amounts
            suspicious_wallets.append(wallet)

    return suspicious_wallets

def detect_high_frequency_trading(transactions, time_window=10, max_trades=5):
    """
    Identifies tokens where transactions happen too frequently in short time periods.
    
    :param transactions: List of transactions with timestamps (in UNIX format)
    :param time_window: Time window in minutes
    :param max_trades: Maximum trades allowed per time window
    :return: List of time windows with suspiciously high activity
    """
    trade_count = defaultdict(int)

    for tx in transactions:
        timestamp = datetime.datetime.fromtimestamp(tx["timestamp"])
        trade_count[timestamp.minute] += 1  # Count trades per minute

    # Find time windows where trades exceed the max allowed
    suspicious_times = [t for t, count in trade_count.items() if count > max_trades]

    return suspicious_times

def detect_circular_trading(transactions):
    """
    Detects circular trading where wallets trade between each other repeatedly.
    
    :param transactions: List of transactions with buyer and seller addresses
    :return: List of suspicious wallet pairs
    """
    trade_pairs = defaultdict(int)

    for tx in transactions:
        buyer = tx["buyer"]
        seller = tx["seller"]
        trade_pairs[(buyer, seller)] += 1

    # Find pairs that trade back and forth multiple times
    suspicious_pairs = [pair for pair, count in trade_pairs.items() if count > 3]

    return suspicious_pairs

def detect_volume_without_price_change(price_data, volume_data):
    """
    Detects tokens with high volume but no significant price movement.
    
    :param price_data: List of token price points over time
    :param volume_data: List of corresponding trading volumes
    :return: Boolean indicating whether wash trading is suspected
    """
    for i in range(1, len(price_data)):
        price_change = abs(price_data[i] - price_data[i - 1])
        volume = volume_data[i]

        if volume > 50000 and price_change < 0.1:  # Arbitrary thresholds
            return True  # Possible wash trading detected

    return False
