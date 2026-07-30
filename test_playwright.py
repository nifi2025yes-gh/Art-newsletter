from playwright.sync_api import sync_playwright

def test_moma_scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.moma.org/calendar/exhibitions", wait_until="domcontentloaded")
        
        # Wait a bit for potential JS execution
        page.wait_for_timeout(3000)
        
        print(f"Title: {page.title()}")
        
        # We need to find exhibition cards. Let's dump some raw HTML to find selectors
        html = page.content()
        with open("moma_raw.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        browser.close()

if __name__ == "__main__":
    test_moma_scrape()
