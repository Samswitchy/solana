from playwright.async_api import async_playwright
#from database import market_to_db, get_all_tokens, holders_to_db
#from database import market_to_db, get_all_tokens, holders_to_db
from modules.database import market_to_db, get_all_tokens, holders_to_db


BASE_URL = "https://solscan.io/token/"

async def get_holders_count(token_address):
    """Fetch holders count from Solscan asynchronously."""
    token_url = f"{BASE_URL}{token_address}#holders"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(token_url, timeout=60000)

            # Wait for page to fully load
            await page.wait_for_timeout(5000)

            try:
                # Extract holders count directly from the element
                element = await page.wait_for_selector(
                    "//html/body/div[1]/div[1]/div[3]/div[1]/div[2]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/div/div",
                    timeout=10000
                )
                holders_count = await element.inner_text()  # Direct text extraction

                print(f"✅ Holders Count for {token_address}: {holders_count}")

            except Exception as e:
                print(f"⚠️ Error extracting holders for {token_address}: {e}")
                holders_count = "Not Available here 2"

            await browser.close()
            return holders_count

    except Exception as e:
        print(f"❌ Error opening Playwright browser: {e}")
        return "Not Available"

#get_holders_count("AVrNeiU54AdXxvpHXkjrMZfpM1v22ZYU94urYH6cpump"

""""
import asyncio
async def main():
    tokens = "89S9RdgynPq5odSRmcCDAzg26iYuRw4wqUmzMbjUpump"
    holders = await get_holders_count(tokens)
    print(holders)

asyncio.run(main())

# ✅ Example usage (must be run inside an async function)
import asyncio
async def main():
    tokens = get_all_tokens()  # Fetch all token addresses

    for token in tokens:  # Iterate over each token
        holders = await get_holders_count(token)
        print(f"Final Holders Count for {token}: {holders}")

asyncio.run(main())
"""