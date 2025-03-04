import requests
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from modules.config import PUMP_API_KEY, PUMP_BASE_URL, RPC_ENDPOINT, PRIVATE_KEY, PUBLIC_KEY

# Define mint_address and amount globally or fetch dynamically
mint_address = "token_address_here"  # Set your token contract address here
amount = 0.01  # Set your buy amount here

def buy_token(mint, amount):
    """
    Executes a buy order for a given token.
    
    :param mint: Token mint address (contract address).
    :param amount: Amount of tokens to buy.
    """
    trade_payload = {
        "publicKey": PUBLIC_KEY,
        "action": "buy",
        "mint": mint,
        "amount": amount,
        "denominatedInSol": "false",
        "slippage": 10,
        "priorityFee": 0.0007, # This amount 0.002 is $0.27 and 0.005 is $0.68
        "pool": "pump"
    }

    try:
        response = requests.post(f"{PUMP_BASE_URL}/trade-local", json=trade_payload)
        response.raise_for_status()
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to PumpPortal API - {e}")
        return
    except ValueError:
        print(f"Error: Invalid JSON response from PumpPortal API - {response.text}")
        return

    if "transaction" not in response_data:
        print(f"Error: No transaction data received - {response_data}")
        return

    try:
        transaction_bytes = bytes.fromhex(response_data["transaction"])
        keypair = Keypair.from_base58_string(PRIVATE_KEY)
        tx = VersionedTransaction(VersionedTransaction.from_bytes(transaction_bytes).message, [keypair])
    except Exception as e:
        print(f"Error while parsing transaction: {e}")
        return

    commitment = CommitmentLevel.Confirmed
    config = RpcSendTransactionConfig(preflight_commitment=commitment)
    tx_payload = SendVersionedTransaction(tx, config)

    try:
        rpc_response = requests.post(
            url=RPC_ENDPOINT,
            headers={"Content-Type": "application/json"},
            data=tx_payload.to_json()
        )
        rpc_response.raise_for_status()
        rpc_data = rpc_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: RPC request failed - {e}")
        return
    except ValueError:
        print(f"Error: RPC response is not valid JSON - {rpc_response.text}")
        return

    tx_signature = rpc_data.get("result")
    if not tx_signature:
        print(f"Error: No transaction signature returned - {rpc_data}")
        return

    print(f'Transaction Successful: https://solscan.io/tx/{tx_signature}')

# Call the function with the predefined values
buy_token(mint_address, amount)
