import pandas as pd
import logging
import sys
import classes as cl
from playwright.sync_api import sync_playwright
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
from io import BytesIO
import config
import export
import ui

# ------------------------------
# Logging Configuration
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("shopee_pipeline.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ShopeePipeline")
logger.info("Application started")

# ------------------------------
# Ingestion Layer (Playwright)
# ------------------------------
def handle_proceed(selected_site, keyword):
    """Handle the Proceed button press with site selection and keyword."""

    if selected_site == "Lazada":
        logger.info(f"User selected Lazada. Starting scrape for: {keyword}")
        records = ingest_with_playwright(keyword)

    elif selected_site == "Shopee":
        logger.info(f"User selected Shopee. Starting scrape for: {keyword}")
        records = ingest_with_playwright(keyword)
        
    elif selected_site == "Amazon":
        logger.info(f"User selected Amazon. Starting scrape for: {keyword}")
        records = ingest_with_playwright(keyword)
        
    else:
        logger.warning(f"Site {selected_site} not yet implemented")
        return

    logger.info(f"Scraped {len(records)} items from {selected_site}")
    

def ingest_with_playwright(keyword, limit=20):
    logger.info(f"Starting Playwright ingestion | keyword='{keyword}', limit={limit}")
    records = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        selected_site = ui.get_selected_site()
        
        
        

        print(f"Scraping {selected_site} for: {keyword}")
        page.goto(config.site_mapping[selected_site].site, timeout=60000)
        page.fill(config.site_mapping[selected_site].search_box, keyword, timeout=60000)
        page.keyboard.press("Enter")

        page.wait_for_selector(config.site_mapping[selected_site].all_items_on_page, timeout=60000)

        items = page.query_selector_all(config.site_mapping[selected_site].all_items_on_page)[:limit]
        print(f"DEBUG: Found {len(items)} items using selector '{config.site_mapping[selected_site].all_items_on_page}'")
        
        print("Checking for sizes ands...")
        

        for item in items:
            try:
                name_elem = item.query_selector(".RfADt a")
                price_elem = item.query_selector(".ooOxS")
                review_elem = item.query_selector(".qzqFw")
                image_elem = item.query_selector(".picture-wrapper img")
                
                if not name_elem or not price_elem:
                    logger.warning("Product name or price selector not found, skipping item")
                    continue
                
                name = name_elem.inner_text()
                price = price_elem.inner_text()
                link = name_elem.get_attribute("href") if name_elem else ""
                if link and not link.startswith("http"):
                    link = config.SITE_MAP[selected_site].site + link
                
                image_url = ""
                if image_elem:
                    image_url = image_elem.get_attribute("src")
                
                review_count = "0"
                if review_elem:
                    review_text = review_elem.inner_text()
                    review_count = review_text.strip("()")  # Remove parentheses

                records.append({
                    "name": name.strip(),
                    "price": price.strip(),
                    "reviews": int(review_count) if review_count.isdigit() else 0,
                    "link": link,
                    "image": image_url
                })
            except Exception:
                logger.warning("Failed to parse one item", exc_info=True)

        browser.close()

    logger.info(f"Ingestion completed | records_collected={len(records)}")
    return records

# ------------------------------
# Data Normalization
# ------------------------------
def normalize_data(records):
    logger.info("Normalizing raw records")

    df = pd.DataFrame(records)

    # crude price extraction (demo-only)
    df["price"] = (
        df["price_raw"]
        .str.extract(r"₱\s*([\d,.]+)")
        .fillna("0")
        .replace(",", "", regex=True)
        .astype(float)
    )

    df.drop(columns=["price_raw"], inplace=True)

    logger.info(f"Normalization completed | rows={len(df)}")
    return df

# ------------------------------
# Ranking Logic
# ------------------------------
def rank_items(df):
    logger.info("Ranking items")

    # Rank by reviews (more reviews = higher score)
    df["score"] = df["reviews"]
    ranked = df.sort_values("score", ascending=False)

    logger.info("Ranking completed")
    return ranked

if __name__ == "__main__":
    import ui