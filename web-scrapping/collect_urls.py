from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random

# BASE_URL = "https://www.etsy.com/search?q=sports+shoes+for+women"
# BASE_URL = "https://www.etsy.com/search?q=shoes+for+men"
BASE_URL = "https://www.etsy.com/search?q=jewelry"

all_links = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled"
        ]
    )

    context = browser.new_context(

        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",

        viewport={"width": 1280, "height": 900},

        locale="en-US",

        java_script_enabled=True
    )

    page = context.new_page()

    for page_num in range(1, 25):

        url = f"{BASE_URL}&page={page_num}"

        print("Opening:", url)

        page.goto(url, timeout=60000)

        # simulate human delay
        time.sleep(random.uniform(3, 6))

        # simulate scroll
        page.mouse.wheel(0, random.randint(3000, 6000))

        time.sleep(random.uniform(2, 4))

        links = page.locator("a[href*='/listing/']").all()

        print("Found:", len(links))

        for link in links:

            href = link.get_attribute("href")

            if href and "/listing/" in href:
                clean_link = href.split("?")[0]
                all_links.append(clean_link)

        time.sleep(random.uniform(5, 10))

    browser.close()

df = pd.DataFrame(all_links, columns=["url"])
df.drop_duplicates(inplace=True)
#df.to_csv("etsy_urls_man_shoes.csv", index=False)
df.to_csv("etsy_urls_accessories.csv", index=False)

print("Saved:", len(df), "URLs")
