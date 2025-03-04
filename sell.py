import requests
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from config import PUMP_API_KEY, PUMP_BASE_URL, RPC_ENDPOINT, PRIVATE_KEY, PUBLIC_KEY

# Define the API request URL with the API key
url = f"{PUMP_BASE_URL}?api-key={PUMP_API_KEY}"

# Trade data
trade_data = {
    "publicKey": PUBLIC_KEY,
    "action": "sell",             # "buy" or "sell"
    "mint": "token CA here",     # Contract address of the token you want to trade
    "amount": 100000,            # Amount of SOL or tokens to trade
    "denominatedInSol": "false", # "true" if amount is in SOL, "false" if number of tokens
    "slippage": 10,              # Percent slippage allowed
    "priorityFee": 0.005,        # Priority fee to enhance transaction speed
    "pool": "pump"               # Exchange to trade on: "pump", "raydium", or "auto"
}

# Send request to Pump Portal API
response = requests.post(url=url, data=trade_data)
if response.status_code != 200:
    print(f"❌ Error: {response.text}")
    exit()

# Load private key from config
keypair = Keypair.from_base58_string(PRIVATE_KEY)

# Construct and sign the transaction
tx_data = response.content  # Raw transaction data from API
tx = VersionedTransaction(VersionedTransaction.from_bytes(tx_data).message, [keypair])

# Define Solana transaction config
commitment = CommitmentLevel.Confirmed
config = RpcSendTransactionConfig(preflight_commitment=commitment)
tx_payload = SendVersionedTransaction(tx, config)

# Send transaction to Solana blockchain
response = requests.post(
    url=RPC_ENDPOINT,
    headers={"Content-Type": "application/json"},
    data=SendVersionedTransaction(tx, config).to_json()
)

# Get transaction signature and display Solscan link
try:
    tx_signature = response.json().get("result")
    if tx_signature:
        print(f"✅ Transaction successful: https://solscan.io/tx/{tx_signature}")
    else:
        print(f"❌ Transaction failed: {response.json()}")
except Exception as e:
    print(f"❌ Error processing transaction: {e}")
