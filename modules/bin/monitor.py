import time
#from modules.marketcap import update_marketcap
from modules.bin.marketcap import update_marketcap

while True:
    update_marketcap()
    time.sleep(300)  # Runs every 5 minutes
