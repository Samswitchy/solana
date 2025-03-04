from playwright.sync_api import sync_playwright

def get_holders_count():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set headless=False for debugging
        page = browser.new_page()
        page.goto("https://solscan.io/token/Ccgn1QqhG3FJpCH6BwhVQ2JJqKr8n72AATnFp1Empump#holders", timeout=60000)

        # Wait for page to load
        page.wait_for_timeout(5000)

        # Execute JavaScript in the page context
        holders_count = page.evaluate("""
            () => {
                let elements = document.querySelectorAll("div.text-neutral5");
                for (let el of elements) {
                    if (el.innerText.toLowerCase().includes('holder')) return el.innerText;
                }
                return null;
            }
        """)

        print("✅ Holders Count:", holders_count if holders_count else "Not Found")
        browser.close()

get_holders_count()
