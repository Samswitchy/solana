import requests
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from modules.config import PUMP_API_KEY, PUMP_BASE_URL, RPC_ENDPOINT, PRIVATE_KEY, PUBLIC_KEY

# Making the request to the PumpPortal API
response = requests.post(url=f"{PUMP_BASE_URL}/trade-local", data={
    "publicKey": PUBLIC_KEY,
    "action": "buy",  # "buy" or "sell"
    "mint": "token CA here",  # contract address of the token you want to trade
    "amount": 100000,  # amount of SOL or tokens to trade
    "denominatedInSol": "false",  # "true" if amount is amount of SOL, "false" if amount is number of tokens
    "slippage": 10,  # percent slippage allowed
    "priorityFee": 0.005,  # amount to use as priority fee
    "pool": "pump"  # exchange to trade on. "pump", "raydium" or "auto"
})

keypair = Keypair.from_base58_string(PRIVATE_KEY)
tx = VersionedTransaction(VersionedTransaction.from_bytes(response.content).message, [keypair])

commitment = CommitmentLevel.Confirmed
config = RpcSendTransactionConfig(preflight_commitment=commitment)
txPayload = SendVersionedTransaction(tx, config)

# Sending the transaction to the RPC endpoint
response = requests.post(
    url=RPC_ENDPOINT,
    headers={"Content-Type": "application/json"},
    data=SendVersionedTransaction(tx, config).to_json()
)

# Extracting the transaction signature
txSignature = response.json()['result']
print(f'Transaction: https://solscan.io/tx/{txSignature}')
