import requests

TELEGRAM_BOT_TOKEN = "8135086500:AAE1_rsvbIHr17i3z3El2oMGnfqx1gnZfjw"
TELEGRAM_CHAT_ID = "5833017299"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    #print(response.status_code, response.json())  # Print API response

#send_telegram_alert("Test message from my bot!")
#send_telegram_alert()