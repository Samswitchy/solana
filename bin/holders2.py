#from playwright.async_api import async_playwright
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import re
#from database import market_to_db, get_all_tokens, holders_to_db
#from database import market_to_db, get_all_tokens, holders_to_db
from modules.database import market_to_db, get_all_tokens, holders_to_db


BASE_URL = "https://solscan.io/token/"

async def get_holders_count(token_address):
    """Fetch holders count from Solscan asynchronously."""
    token_url = f"{BASE_URL}{token_address}#holders"

 
    try:
        async with async_playwright() as p:
            # 🔹 Create a Browser Context to Set a Fake User-Agent
            browser = await p.chromium.launch(headless=True)  # Change to False for debugging
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            await page.goto(token_url, timeout=60000)  # Load page
            await page.wait_for_timeout(5000)  # Wait for content

            holders_count = "Not Available"

            # 🔹 Retry up to 3 times if element is not found
            for attempt in range(3):
                try:
                    element = await page.wait_for_selector("div:has-text('Total')", timeout=15000)
                    text = await element.inner_text()
                    #holders_count = await element.inner_text()
                    #print(text)
                    # Extract only the number
                    match = re.search(r'Total\s([\d,]+)\s+holder\(s\)', text)
                    if match:
                        holders_count = match.group(1).replace(',', '')  # Remove commas
                        return int(holders_count)
                    else:
                        return None

                    print(f"✅ Holders Count: {holders_count}")
                    break  # Exit loop if successful

                except PlaywrightTimeoutError:
                    print(f"⚠️ Attempt {attempt+1}: Holders count element not found, retrying...")

            await browser.close()
            return holders_count

    except Exception as e:
        print(f"❌ Error opening Playwright browser: {e}")
        return "Not Available"

#get_holders_count("AVrNeiU54AdXxvpHXkjrMZfpM1v22ZYU94urYH6cpump"
"""
import asyncio
async def main():
    tokens = "6gJU76K4g7Xk9v56e8EfNr44oB9bNRPd3izcVNagpump"
    #tokens = get_all_tokens()
    holders = await get_holders_count(tokens)
    print(holders)

asyncio.run(main())

"""
# ✅ Example usage (must be run inside an async function)
import asyncio
async def main():
    tokens = get_all_tokens()  # Fetch all token addresses
    #tokens = "89S9RdgynPq5odSRmcCDAzg26iYuRw4wqUmzMbjUpump"  # Fetch all token addresses

    for token in tokens:  # Iterate over each token
        print(token)
        holders = await get_holders_count(token)

        print(f"Final Holders Count for {token}: {holders}")

asyncio.run(main())

