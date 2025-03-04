from playwright.sync_api import sync_playwright
from database import get_all_tokens

def get_holders_count(token_address):
    url = f"https://solscan.io/token/{token_address}#holders"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        try:
            # Locate holders count using XPath
            element = page.wait_for_selector(
                "//html/body/div[1]/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/div/div", 
                timeout=10000
            )
            holders_count = element.inner_text().strip()
            print(f"✅ Holders Count for {token_address}: {holders_count}")
        except Exception as e:
            print(f"❌ Error fetching holders count for {token_address}: {e}")
            holders_count = None

        browser.close()
        return holders_count  # Return the holder count

def fetch_all_holders():
    token_addresses = get_all_tokens()  # Fetch all tokens from the database
    holders_data = {}

    for token in token_addresses:
        holders_count = get_holders_count(token)  # Process one token at a time
        holders_data[token] = holders_count

        # Optional: Save results to database or log
        # save_to_db(token, holders_count)

    #return holders_data  # Returns a dictionary of token: holders_count

# Example call
holders_info = fetch_all_holders()
print(holders_info)

def fetch_holders()
token_addresses = get_all_tokens()

# Iterate through each token and get holders count
for token in token_addresses:
    get_holders_count(token)