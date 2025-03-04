import requests
from modules.config import PUMP_API_KEY, PUMP_BASE_URL

# Define the request URL with the API key
url = f"{PUMP_BASE_URL}?api-key={PUMP_API_KEY}"

# Define trade data
trade_data = {
    "action": "buy",             # "buy" or "sell"
    "mint": "your CA here",      # contract address of the token you want to trade
    "amount": 100000,            # amount of SOL or tokens to trade
    "denominatedInSol": "false", # "true" if amount is amount of SOL, "false" if amount is number of tokens
    "slippage": 10,              # percent slippage allowed
    "priorityFee": 0.00005,      # amount used to enhance transaction speed
    "pool": "pump"               # exchange to trade on. "pump", "raydium" or "auto"
}

# Send POST request
response = requests.post(url=url, data=trade_data)

# Process response
data = response.json()
print(data)  # Tx signature or error(s)
