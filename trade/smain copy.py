from asell import sell_token

def main():
    input_mint = "TOKEN_MINT_ADDRESS_HERE"  # Replace with actual token mint
    output_mint = "So11111111111111111111111111111111111111112"  # Default: Selling for SOL
    sell_amount = 1.0  # Amount of tokens to sell
    priority_fee = 0.0007  # Optional priority fee

    txid, received = sell_token(input_mint, output_mint, sell_amount, priority_fee)

    if txid:
        print(f"✅ Transaction Successful: {txid}")
        print(f"💰 Received: {received} tokens/SOL")
    else:
        print("❌ Transaction failed.")

if __name__ == "__main__":
    main()
