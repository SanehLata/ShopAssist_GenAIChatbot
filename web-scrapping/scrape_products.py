import sqlite3
import pandas as pd
import time
import random

from playwright.sync_api import sync_playwright

# -----------------------------
# CONFIG
# -----------------------------

CSV_FILE = "etsy_urls.csv"
DB_FILE = "etsy_products.db"

MIN_DELAY = 8
MAX_DELAY = 18

BLOCK_DELAY_MIN = 30
BLOCK_DELAY_MAX = 60


# -----------------------------
# LOAD URLS
# -----------------------------

df = pd.read_csv(CSV_FILE)
urls = df["url"].drop_duplicates().tolist()

print(f"Total URLs in CSV: {len(urls)}")


# -----------------------------
# DATABASE SETUP
# -----------------------------

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    url TEXT PRIMARY KEY,
    title TEXT,
    price TEXT,
    shop TEXT,
    rating TEXT,
    review_count TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# -----------------------------
# GET ALREADY SCRAPED URLS
# -----------------------------

cursor.execute("SELECT url FROM products")
scraped_urls = set(row[0] for row in cursor.fetchall())

print(f"Already scraped: {len(scraped_urls)}")

urls_to_scrape = [u for u in urls if u not in scraped_urls]

print(f"Remaining to scrape: {len(urls_to_scrape)}")


# -----------------------------
# PLAYWRIGHT SCRAPER
# -----------------------------

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(

        user_data_dir="playwright_profile",

        headless=False,

        args=[
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
        ]
    )

    page = context.new_page()

    for i, url in enumerate(urls_to_scrape):

        print(f"\nScraping {i+1}/{len(urls_to_scrape)}")
        print(url)

        try:

            page.goto(url, timeout=60000)

            time.sleep(random.uniform(5, 9))


            # -----------------------------
            # BLOCK DETECTION
            # -----------------------------

            content = page.content()

            if "Access is temporarily restricted" in content:

                print("BLOCKED — waiting longer")

                time.sleep(random.uniform(
                    BLOCK_DELAY_MIN,
                    BLOCK_DELAY_MAX
                ))

                continue


            # -----------------------------
            # HUMAN SIMULATION
            # -----------------------------

            page.mouse.wheel(0, random.randint(300, 1000))

            time.sleep(random.uniform(2, 5))


            # -----------------------------
            # SAFE ELEMENT EXTRACTION
            # -----------------------------

            try:
                page.wait_for_selector("h1", timeout=15000)
                title = page.locator("h1").first.inner_text()
            except:
                title = ""


            try:
                price = page.locator(
                    "[data-buy-box-region='price'] p"
                ).first.inner_text()
            except:
                price = ""


            try:
                shop = page.locator(
                    "a[href*='shop']"
                ).first.inner_text()
            except:
                shop = ""


            try:
                rating = page.locator(
                    "[data-buy-box-region='review-rating']"
                ).inner_text()
            except:
                rating = ""


            try:
                review_count = page.locator(
                    "[data-buy-box-region='review-count']"
                ).inner_text()
            except:
                review_count = ""


            # -----------------------------
            # SAVE TO DATABASE
            # -----------------------------

            cursor.execute("""
            INSERT OR IGNORE INTO products
            (url, title, price, shop, rating, review_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                url,
                title,
                price,
                shop,
                rating,
                review_count
            ))

            conn.commit()

            print("Saved:", title[:60])


            # -----------------------------
            # HUMAN DELAY
            # -----------------------------

            delay = random.uniform(MIN_DELAY, MAX_DELAY)

            print(f"Sleeping {delay:.1f} sec")

            time.sleep(delay)


        except Exception as e:

            print("Error:", e)

            time.sleep(random.uniform(10, 20))


    context.close()

conn.close()

print("\nScraping complete.")
