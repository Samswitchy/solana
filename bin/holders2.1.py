from playwright.sync_api import sync_playwright
from database import get_all_tokens

# Base URL for Solscan token holders page
BASE_URL = "https://solscan.io/token/"

def get_holders_count(token_adds):
    token_url = f"{BASE_URL}{token_adds}#holders"  # Combine base URL and token address
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Use headless=False for debugging
        page = browser.new_page()
        page.goto(token_url, timeout=60000)

        # Wait for page to fully load
        page.wait_for_timeout(5000)

        # Use XPath to find the holders count element
        element = page.wait_for_selector("//html/body/div[1]/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/div/div", timeout=10000)
        holders_count = element.inner_text()

        print(f"✅ Holders Count for here {token_adds}: {holders_count}")
        browser.close()

# Example usage
#get_holders_count("B8UruRxFvAoTZoSg7waHFkGJ96nHPso5VbEkVAzapump")
"""
# Fetch token addresses from database and get holders count for each token
token_addresses = get_all_tokens()
for token in token_addresses:
    get_holders_count(token)

"""
