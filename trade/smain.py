from asell import sell_token

# Example usage
TOKEN_MINT = "Your_Token_Address_Here"
txid, received_sol = sell_token(TOKEN_MINT, sol_amount=100)  # Selling 100 tokens

if txid:
    print(f"✅ Sold successfully! Tx ID: {txid}")
    print(f"🔹 Received: {received_sol} SOL")
else:
    print("❌ Sell transaction failed.")
