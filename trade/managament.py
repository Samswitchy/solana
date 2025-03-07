import time
from core.db import get_token_price

def take_profit(buy_price: float, current_price: float, profit_multiplier: float = 2.5) -> bool:
    """
    Checks if the token price has reached the target profit level.
    :param buy_price: The price at which the token was bought.
    :param current_price: The current market price of the token.
    :param profit_multiplier: The multiplier for take-profit (default: 2.5x).
    :return: True if take-profit condition is met, False otherwise.
    """
    target_price = buy_price * profit_multiplier
    return current_price >= target_price

def stop_loss(buy_price: float, current_price: float, stop_loss_percentage: float = 0.3) -> bool:
    """
    Checks if the token price has dropped below the stop-loss threshold.
    :param buy_price: The price at which the token was bought.
    :param current_price: The current market price of the token.
    :param stop_loss_percentage: The percentage drop to trigger stop-loss (default: 30%).
    :return: True if stop-loss condition is met, False otherwise.
    """
    stop_loss_price = buy_price * (1 - stop_loss_percentage)
    return current_price <= stop_loss_price

if __name__ == "__main__":
    # Example usage
    buy_price = 1.0  # Example buy price
    current_price = get_token_price("TOKEN_MINT_ADDRESS_HERE")
    
    if take_profit(buy_price, current_price):
        print("✅ Take profit triggered!")
    elif stop_loss(buy_price, current_price):
        print("❌ Stop loss triggered!")
    else:
        print("ℹ️ Holding position.")
