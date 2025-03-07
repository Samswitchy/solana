import requests
import numpy as np
import talib
import time

# Function to fetch all pair addresses for a token
def fetch_pair_addresses(token_address):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    
    try:
        response = requests.get(url)
        data = response.json()

        if "pairs" in data and len(data["pairs"]) > 0:
            pair_addresses = [pair["pairAddress"] for pair in data["pairs"]]
            return pair_addresses
        else:
            print("❌ No pairs found for this token.")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

# Function to fetch historical price data for a pair
def fetch_price_history(pair_address, limit=50):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"

    try:
        response = requests.get(url)
        data = response.json()

        if "pairs" in data and len(data["pairs"]) > 0:
            pair_data = data["pairs"][0]
            prices = []

            # Extract historical prices from trade history
            if "trades" in pair_data:
                trades = pair_data["trades"]
                prices = [float(trade["priceUsd"]) for trade in trades[:limit]]  # Get last `limit` prices

            return prices[::-1] if prices else None  # Reverse list to maintain order
        else:
            print(f"❌ No historical price data for pair {pair_address}.")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

# Function to calculate RSI
def calculate_rsi(prices, period=14):
    prices = np.array(prices, dtype=float)
    rsi = talib.RSI(prices, timeperiod=period)
    return rsi[-1] if len(rsi) > 0 else None

# Function to calculate Bollinger Bands
def calculate_bollinger_bands(prices, period=20, std_dev=2):
    prices = np.array(prices, dtype=float)
    upper, middle, lower = talib.BBANDS(prices, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev, matype=0)
    return upper[-1], middle[-1], lower[-1]

# Function to calculate Moving Averages
def calculate_moving_average(prices, period=50):
    prices = np.array(prices, dtype=float)
    ma = talib.SMA(prices, timeperiod=period)
    return ma[-1] if len(ma) > 0 else None

# Main function to process a token
def analyze_token(token_address):
    pair_addresses = fetch_pair_addresses(token_address)

    if not pair_addresses:
        print("⚠️ No valid pairs found.")
        return

    for pair in pair_addresses:
        print(f"\n🔹 Checking pair: {pair}")
        price_history = fetch_price_history(pair)

        if price_history and len(price_history) >= 20:
            rsi_value = calculate_rsi(price_history)
            upper_band, middle_band, lower_band = calculate_bollinger_bands(price_history)
            moving_average = calculate_moving_average(price_history)

            print(f"📊 RSI: {rsi_value}")
            print(f"📊 Bollinger Bands - Upper: {upper_band}, Middle: {middle_band}, Lower: {lower_band}")
            print(f"📊 Moving Average: {moving_average}")

            # ✅ Buy Signal Conditions
            if rsi_value < 30 and price_history[-1] > lower_band and price_history[-1] > moving_average:
                print("🚀 BUY SIGNAL TRIGGERED!")
            else:
                print("⏳ No buy signal yet.")
        else:
            print(f"⚠️ Not enough historical data for pair {pair}. Waiting and retrying...")
            time.sleep(2)  # Wait a few seconds before retrying

# 🔥 Example usage
token_address = "59LC5TjNaT4JUBXhf6dhHKPLrJB9QERdKetqc8eCpump"  # Replace with actual token address
analyze_token(token_address)
