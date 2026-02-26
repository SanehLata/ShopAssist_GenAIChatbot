import sqlite3
import pandas as pd
import time
import random
import json
import re
import logging
from datetime import datetime

from playwright.sync_api import sync_playwright


# ============================================================
# CONFIG
# ============================================================

CSV_FILE = "etsy_urls_accessories.csv"
DB_FILE = "etsy_products.db"
LOG_FILE = "etsy_scraper_accessories.log"

MIN_DELAY = 6
MAX_DELAY = 15

BLOCK_DELAY_MIN = 30
BLOCK_DELAY_MAX = 60

MAX_RETRIES = 3


# ============================================================
# LOGGING SETUP
# ============================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ============================================================
# SAFE STRING CONVERSION
# ============================================================

def safe_str(value):

    if value is None:
        return None

    if isinstance(value, (dict, list)):
        return json.dumps(value)

    return str(value)


# ============================================================
# LOAD URLS
# ============================================================

df = pd.read_csv(CSV_FILE)

urls = (
    df["url"]
    .drop_duplicates()
    .dropna()
    .tolist()
)

print(f"Total URLs in CSV: {len(urls)}")


# ============================================================
# DATABASE SETUP (ADDED review_count COLUMN)
# ============================================================

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (

    product_id INTEGER PRIMARY KEY AUTOINCREMENT,

    url TEXT UNIQUE,

    title TEXT,
    description TEXT,

    price TEXT,
    currency TEXT,

    availability TEXT,

    rating TEXT,
    review_count TEXT,

    category TEXT,

    scraped_at TEXT

)
""")

conn.commit()


# ============================================================
# RESUME SUPPORT (BASED ON URL)
# ============================================================

cursor.execute("SELECT url FROM products")

scraped_urls = set(row[0] for row in cursor.fetchall())

urls_to_scrape = [u for u in urls if u not in scraped_urls]

print(f"Remaining to scrape: {len(urls_to_scrape)}")


# ============================================================
# MAIN SCRAPER
# ============================================================

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir="playwright_profile",
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled"
        ]
    )

    page = context.new_page()

    for index, url in enumerate(urls_to_scrape):

        print(f"\nScraping {index+1}/{len(urls_to_scrape)}")
        print(url)

        success = False

        for attempt in range(MAX_RETRIES):

            try:

                page.goto(url, timeout=60000)

                time.sleep(random.uniform(4, 8))

                content = page.content()

                if "Access is temporarily restricted" in content:

                    print("BLOCKED - waiting")
                    time.sleep(random.uniform(
                        BLOCK_DELAY_MIN,
                        BLOCK_DELAY_MAX
                    ))
                    continue


                # -----------------------------------------
                # DEFAULT VALUES
                # -----------------------------------------

                title = None
                description = None

                price = None
                currency = None

                availability = None
                rating = None
                review_count = None

                category = None

                scraped_at = datetime.now().isoformat()


                # -----------------------------------------
                # JSON-LD EXTRACTION
                # -----------------------------------------

                json_elements = page.locator(
                    "script[type='application/ld+json']"
                ).all()

                for element in json_elements:

                    try:

                        raw = element.inner_text()

                        data = json.loads(raw)

                        if isinstance(data, list):
                            data = data[0]

                        if data.get("@type") == "Product":

                            title = data.get("name")

                            description = data.get("description")

                            category = data.get("category")

                            offers = data.get("offers", {})

                            if isinstance(offers, list):
                                offers = offers[0]

                            price = offers.get("price")

                            currency = offers.get("priceCurrency")

                            availability = offers.get("availability")

                            agg = data.get("aggregateRating", {})

                            rating = agg.get("ratingValue")
                            review_count = agg.get("reviewCount")

                            break

                    except:
                        pass


                # -----------------------------------------
                # FALLBACK TITLE
                # -----------------------------------------

                if not title:

                    try:
                        title = page.locator("h1").first.inner_text()
                    except:
                        pass


                # -----------------------------------------
                # SAVE TO DATABASE (UPDATED INSERT)
                # -----------------------------------------

                cursor.execute("""
                INSERT OR IGNORE INTO products (

                    url,
                    title,
                    description,
                    price,
                    currency,
                    availability,
                    rating,
                    review_count,
                    category,
                    scraped_at

                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (

                    safe_str(url),

                    safe_str(title),
                    safe_str(description),

                    safe_str(price),
                    safe_str(currency),

                    safe_str(availability),

                    safe_str(rating),
                    safe_str(review_count),

                    safe_str(category),

                    safe_str(scraped_at)

                ))

                conn.commit()

                print("Saved:", title)

                logging.info(f"SUCCESS: {url}")

                success = True

                break


            except Exception as e:

                print("Retry error:", e)

                logging.error(f"ERROR {url}: {e}")

                time.sleep(random.uniform(5, 12))


        if not success:

            logging.error(f"FAILED AFTER RETRIES: {url}")


        delay = random.uniform(MIN_DELAY, MAX_DELAY)

        print(f"Sleeping {delay:.1f} sec")

        time.sleep(delay)


    context.close()


conn.close()

print("\nDONE")