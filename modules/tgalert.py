import requests

TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

# Inside analyze_wash_trading():
if suspicious_wallets or suspicious_times or suspicious_pairs:
    alert_message = f"🚨 Wash trading detected for {contract_address}!\nWallets: {suspicious_wallets}"
    send_telegram_alert(alert_message)
