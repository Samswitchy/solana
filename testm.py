import requests
import numpy as np
import talib

# Function to fetch real-time price data from Jupiter API
def fetch_price_data(token_address):
    url = f"https://quote-api.jup.ag/v6/quote?inputMint={token_address}&outputMint=So11111111111111111111111111111111111111112&amount=1000000"
    try:
        response = requests.get(url).json()
        
        if "outAmount" in response:
            price = float(response["outAmount"]) / 1e9  # Convert lamports to SOL
            return price
        else:
            print("Error fetching price data.")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
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

# Token Address (Replace with your token's address)
token_address = "5dyma5yb1tqyxkctowbbvq6ahhyvr3jyxyn5k7wpplkq"

# Fetch historical price data
price_history = [fetch_price_data(token_address) for _ in range(50)]  # Fetch last 50 prices
price_history = [p for p in price_history if p is not None]  # Remove None values

# Check if enough data is available to calculate indicators
if len(price_history) >= 20:
    rsi_value = calculate_rsi(price_history)
    upper_band, middle_band, lower_band = calculate_bollinger_bands(price_history)
    moving_average = calculate_moving_average(price_history)
    
    print(f"RSI: {rsi_value}")
    print(f"Bollinger Bands - Upper: {upper_band}, Middle: {middle_band}, Lower: {lower_band}")
    print(f"Moving Average: {moving_average}")
    
    # **Buy Signal Conditions**
    if rsi_value < 30 and price_history[-1] > lower_band and price_history[-1] > moving_average:
        print("✅ BUY SIGNAL TRIGGERED!")
    else:
        print("❌ No buy signal yet.")
else:
    print("⚠️ Not enough data to calculate indicators.")
