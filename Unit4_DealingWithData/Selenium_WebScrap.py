import os
import time
import csv
import threading
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

# ────────────────────────────────────────
# SETUP
# ────────────────────────────────────────

# Setup Chrome options
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Uncomment for background mode
driver = webdriver.Chrome(options=options)

# Target website
URL = "http://quotes.toscrape.com/scroll"

# Create folders for output
CSV_FILENAME = 'scroll_quotes_images.csv'
IMAGES_FOLDER = 'downloaded_images'

os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Open CSV for writing
csv_file = open(CSV_FILENAME, 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Quote', 'Author', 'Image_Filename'])

# ────────────────────────────────────────
# IMAGE DOWNLOADING (Multithreading)
# ────────────────────────────────────────

def download_image(img_url, filename):
    """Downloads a single image and saves it locally."""
    try:
        img_data = requests.get(img_url).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)
    except Exception as e:
        print(f"[ERROR] Failed to download image {img_url}: {e}")

# ────────────────────────────────────────
# SCRAPING FUNCTIONS
# ────────────────────────────────────────

def scrape_visible_quotes(existing_quotes):
    """Scrapes all visible quotes and images on the page."""
    quotes = driver.find_elements(By.CSS_SELECTOR, ".quote")

    for idx, quote in enumerate(quotes):
        try:
            text = quote.find_element(By.CSS_SELECTOR, ".text").text
            author = quote.find_element(By.CSS_SELECTOR, ".author").text

            # Avoid duplicates
            if (text, author) in existing_quotes:
                continue
            existing_quotes.add((text, author))

            # Find image if exists
            try:
                img_element = quote.find_element(By.CSS_SELECTOR, "img")
                img_url = img_element.get_attribute('src')
                img_filename = f"{IMAGES_FOLDER}/quote_{idx}.jpg"

                # Download image using a thread
                threading.Thread(target=download_image, args=(img_url, img_filename)).start()
            except:
                img_filename = "no_image_found"

            # Write to CSV
            csv_writer.writerow([text, author, img_filename])

        except Exception as e:
            print(f"[WARNING] Skipping broken quote block: {e}")

# ────────────────────────────────────────
# MAIN SCRAPING LOGIC
# ────────────────────────────────────────

def scrape_infinite_scroll():
    """Handles scrolling, scraping, and retry logic."""
    driver.get(URL)
    time.sleep(2)  # Wait for initial page load

    scraped_quotes = set()
    scrape_visible_quotes(scraped_quotes)

    scroll_retries = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)  # Wait for new content to load

        scrape_visible_quotes(scraped_quotes)

        # Check if page height increased
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            scroll_retries += 1
            print(f"[INFO] No scroll progress. Retry {scroll_retries}/3...")
            if scroll_retries >= 3:
                print("[INFO] No more content. Ending scraping.")
                break
        else:
            scroll_retries = 0
            last_height = new_height

# ────────────────────────────────────────
# RUN
# ────────────────────────────────────────

if __name__ == "__main__":
    try:
        scrape_infinite_scroll()
    finally:
        # Cleanup
        driver.quit()
        csv_file.close()
        print(f"[DONE] Scraping completed. Data saved to '{CSV_FILENAME}'. Images saved to '{IMAGES_FOLDER}/'.")
