import os

API_ID = "19780264"
API_HASH = "cbb43586ab6e93107ac5cc6fd741c869"
PHONE_NUMBER = "+2348116267294"
CHANNEL_USERNAME = "pfultimate"

#CHANNEL_USERNAME = "pfultimate"



""" THIS IS PUMPFUN CODE TO BUY TOKEN 
#This is the transaction details for the buy or sell order
# PumpPortal API Configuration
PUMP_API_KEY = "65gmyd1h98nncx3ca9u6wtv48num6d315dn6uvuu70v4gp9f91k6ygtjf5p6pv2dcx87gwtjf575eh319hh4uxa78t26yx2j70nncubt8nu3ax9rd50pjckf90qk0hvedmv54p3m84yku6ct42gvjd91mjrk7b5tpckj7a899b6wv399nq4ymu770v6wmvp6hx7ccv2b58kuf8"
PUMP_BASE_URL = "https://pumpportal.fun/api/trade"
PRIVATE_KEY = "3W6M4K1oMP8VFq3wSk6vZkWvpn9BUi2NXrCbUeonPYDjHw9AydhABdfyuJKAeumSPdobjy5XqicLTv1qf4dt7GmV"

# Solana Configuration
RPC_ENDPOINT = "https://api.mainnet-beta.solana.com/"  # Replace with your Solana RPC endpoint
PRIVATE_KEY = "y3W6M4K1oMP8VFq3wSk6vZkWvpn9BUi2NXrCbUeonPYDjHw9AydhABdfyuJKAeumSPdobjy5XqicLTv1qf4dt7GmV"
PUBLIC_KEY = "2n88tYFficXyTUqTc8EWKBnTRDoBvuQcfKYLA7b5hyc3"

# Construct the Solscan URL dynamically
SOLBASE_URL = "https://solscan.io/token/"

"""



# config.py
HELIUS_RPC_URL = "https://mainnet.helius-rpc.com/?api-key=ac513469-f955-473a-9b73-9391b9113f7d"
HELIUS_WS_URL = "wss://mainnet.helius-rpc.com/?api-key=ac513469-f955-473a-9b73-9391b9113f7d"

# Your Solana Wallet Private Key (IMPORTANT: Keep this secret)
PRIVATE_KEY = "3W6M4K1oMP8VFq3wSk6vZkWvpn9BUi2NXrCbUeonPYDjHw9AydhABdfyuJKAeumSPdobjy5XqicLTv1qf4dt7GmV"




# Define the folder path for the database
#FOLDER_PATH = "files"
FOLDER_PATH = "/Users/user/Documents/Project X/Ai/Sia/modules/files"

# Ensure the folder exists
if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)

# Set the database path inside the folder
DATABASE_NAME = os.path.join(FOLDER_PATH, "tokens.db")
TRADE = os.path.join(FOLDER_PATH, "trades.db")
GRADUATING = os.path.join(FOLDER_PATH, "graduating.db")

TELEGRAM_DATA = os.path.join(FOLDER_PATH, "telegramData_session")

 