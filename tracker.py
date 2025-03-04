import asyncio
from solana.rpc.websocket_api import connect, LogsSubscribeFilterMentions

from solana.rpc.api import Client

# Constants
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
WALLET_ADDRESS = "552erowhnx9kBkQUq7DaFtof4SA8AbkBKF1DunbAL7u2"

# Solana Client
solana_client = Client(SOLANA_RPC_URL)

async def watch_wallet():
    async with connect("wss://api.mainnet-beta.solana.com") as ws:
        # ✅ Correct usage of LogsSubscribeFilterMentions
        #await ws.logs_subscribe(LogsSubscribeFilterMentions(WALLET_ADDRESS))
        await ws.logs_subscribe({"mentions": WALLET_ADDRESS})

        print(f"Listening for transactions from {WALLET_ADDRESS}...")

        while True:
            msg = await ws.recv()
            if msg and "params" in msg:
                logs = msg["params"]["result"]
                tx_signature = logs["signature"]
                print(f"🔍 New Transaction: {tx_signature}")

                # Fetch transaction details
                trade_data = get_transaction_details(tx_signature)

                # Extract program IDs
                program_ids = extract_program_ids(trade_data)
                print(f"📜 Detected Program IDs: {program_ids}")

                # Identify trading platform
                category = categorize_trade(program_ids)
                print(f"🚀 Trade Platform: {category}")

def get_transaction_details(tx_signature):
    """Fetch transaction details from Solana RPC."""
    tx = solana_client.get_transaction(tx_signature, "jsonParsed")
    return tx

def extract_program_ids(transaction):
    """Extract all program IDs from transaction instructions."""
    program_ids = set()
    try:
        instructions = transaction["result"]["transaction"]["message"]["instructions"]
        for instr in instructions:
            if "programId" in instr:
                program_ids.add(instr["programId"])
    except KeyError:
        pass
    return list(program_ids)

def categorize_trade(program_ids):
    """Identify the platform based on program IDs."""
    for program_id in program_ids:
        if "pmp" in program_id.lower():  # Example check for Pump.fun
            return "Pump.fun"
        elif "raydium" in program_id.lower():
            return "Raydium"
        elif "jup" in program_id.lower():
            return "Jupiter"
    return "Unknown Platform"

# Run the wallet tracker
asyncio.run(watch_wallet())
