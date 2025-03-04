from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from config import SOLBASE_URL

# Define the token address separately
TOKEN_ADDRESS = "AVrNeiU54AdXxvpHXkjrMZfpM1v22ZYU94urYH6cpump"

# Construct the Solscan URL dynamically
url = f"{SOLBASE_URL}{TOKEN_ADDRESS}#holders"

# Set up Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without opening a browser
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the Solscan page
driver.get(url)

# Wait for JavaScript to load content
time.sleep(5)  # Adjust if needed

# Execute JavaScript to find the correct element
holders_count = driver.execute_script("""
    let elements = document.querySelectorAll("div.text-neutral5");
    for (let el of elements) {
        if (el.innerText.includes('holder')) return el.innerText;
    }
    return null;
""")

if holders_count:
    #print(f"✅ Holders Count for {TOKEN_ADDRESS}: {holders_count}")
    print("✅ Holders Count:", holders_count)
else:
    print(f"❌ Could not extract holders count for {TOKEN_ADDRESS}")

# Close the browser
driver.quit()
