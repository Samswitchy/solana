import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import SOLBASE_URL

async def get_holders_count(token_address):
    """
    Fetches the holders count for a given Solana token from Solscan.
    
    Args:
        token_address (str): The Solana token address.

    Returns:
        str: Holders count as a string (e.g., '503 holder(s)') or None if not found.
    """
    url = f"{SOLBASE_URL}{token_address}#holders"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load content

        holders_count = driver.execute_script("""
            let elements = document.querySelectorAll("div.text-neutral5");
            for (let el of elements) {
                if (el.innerText.includes('holder')) return el.innerText;
            }
            return null;
        """)

        return holders_count

    except Exception as e:
        print(f"❌ Error fetching holders count for {token_address}: {e}")
        return None

    finally:
        driver.quit()
