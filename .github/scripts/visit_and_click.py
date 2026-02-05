from playwright.sync_api import sync_playwright, TimeoutError

URL = "https://financial-assets-insights.streamlit.app"
# <button type="button" class="_button_qx90d_1 _button_primary_qx90d_26 _restartButton_2xb9v_14"
#         data-testid="wakeup-button-viewer">Yes, get this app back up!</button>
BUTTON_SELECTOR = "text=Yes, get this app back up!"  

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle", timeout=60000)

        try:
            page.wait_for_selector(BUTTON_SELECTOR, timeout=5000)
            print("Button found, clicking...")
            page.click(BUTTON_SELECTOR)
            page.wait_for_timeout(2000)
        except TimeoutError:
            print("Button not found, continuing without clicking.")

        browser.close()

if __name__ == "__main__":
    print("Install browser if doesn't exist: 'playwright install chromium-headless-shell'")
    main()
