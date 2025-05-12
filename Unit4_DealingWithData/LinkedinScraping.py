import os
import time
import random
import csv
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ─────────────────────────────────────
# SETUP
# ─────────────────────────────────────

username = input("Enter your LinkedIn email: ")
password = getpass.getpass("Enter your LinkedIn password (hidden): ")

print("\nChoose section to scrape:")
print("1 - Home Feed")
print("2 - Jobs")
choice = input("Enter the number of the section you want to scrape: ")

search_keyword = ""
search_location = ""
if choice == '2':
    search_keyword = input("Enter the job title you want to search for (example: AI Engineer): ").strip()
    search_location = input("Enter the location/country (example: United States): ").strip()
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_keyword.replace(' ', '%20')}&location={search_location.replace(' ', '%20')}"

options = Options()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

output_folder = "linkedin_scrape"
os.makedirs(output_folder, exist_ok=True)

csv_filename = os.path.join(output_folder, "linkedin_jobs_data.csv")
csv_file = open(csv_filename, "w", newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Job Title", "Company", "Location", "Employment Type", "Date Posted", "Job URL", "Full Description"])

# ─────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────

def login_to_linkedin():
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password + Keys.RETURN)
    time.sleep(5)

def navigate_to_section(choice):
    if choice == '1':
        driver.get("https://www.linkedin.com/feed/")
    elif choice == '2':
        driver.get(search_url)
    else:
        print("[ERROR] Invalid choice!")
        driver.quit()
        exit()
    time.sleep(5)

def scroll_jobs_page():
    """Scroll the full page (not sidebar) to load more jobs."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2.0, 3.5))

def is_easy_apply_job():
    """Check inside job detail page if Easy Apply exists."""
    try:
        driver.find_element(By.CSS_SELECTOR, "button.jobs-apply-button")
        return True
    except:
        return False
def scrape_job_from_card(job_card, idx):
    """Click job card, check for Easy Apply, scrape if possible."""
    try:
        driver.execute_script("arguments[0].scrollIntoView();", job_card)
        job_card.click()
        time.sleep(random.uniform(2.5, 4.5))

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-details__main-content")))

        if not is_easy_apply_job():
            print(f"[INFO] Job {idx+1} is not Easy Apply. Skipping.")
            return

        print(f"[INFO] Scraping Easy Apply job {idx+1}.")

        try:
            job_title = driver.find_element(By.CSS_SELECTOR, "h2.jobs-unified-top-card__job-title").text
        except:
            try:
                job_title = driver.find_element(By.CSS_SELECTOR, "h1.top-card-layout__title").text
            except:
                job_title = "N/A"

        try:
            company = driver.find_element(By.CSS_SELECTOR, "span.jobs-unified-top-card__company-name").text
        except:
            try:
                company = driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link").text
            except:
                company = "N/A"

        try:
            location = driver.find_element(By.CSS_SELECTOR, "span.jobs-unified-top-card__bullet").text
        except:
            try:
                location = driver.find_element(By.CSS_SELECTOR, "span.topcard__flavor--bullet").text
            except:
                location = "N/A"

        try:
            employment_type = driver.find_element(By.XPATH, "//span[text()='Employment type']/following-sibling::span").text
        except:
            employment_type = "N/A"

        try:
            date_posted = driver.find_element(By.CSS_SELECTOR, "span.jobs-unified-top-card__posted-date").text
        except:
            try:
                date_posted = driver.find_element(By.CSS_SELECTOR, "span.posted-time-ago__text").text
            except:
                date_posted = "N/A"

        try:
            description = driver.find_element(By.CSS_SELECTOR, "div.jobs-description__content").text
        except:
            description = "N/A"

        try:
            job_url = driver.current_url
        except:
            job_url = "N/A"

        csv_writer.writerow([job_title, company, location, employment_type, date_posted, job_url, description])
        print(f"[INFO] Successfully scraped Job {idx+1}: {job_title}")

    except Exception as e:
        print(f"[WARNING] Failed to scrape job {idx+1}: {e}")



def infinite_scraping():
    """Infinite scraping session. Ctrl+C to stop."""
    print("[INFO] Infinite scraping started. Press Ctrl+C to stop manually.")
    scraped_jobs = set()

    while True:
        try:
            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container--clickable")
            print(f"[INFO] Found {len(job_cards)} job cards.")

            for idx, job_card in enumerate(job_cards):
                if idx in scraped_jobs:
                    continue
                scrape_job_from_card(job_card, idx)
                scraped_jobs.add(idx)
                time.sleep(random.uniform(2.5, 4.0))

            scroll_jobs_page()

        except KeyboardInterrupt:
            print("[INFO] Manual stop requested (Ctrl+C). Exiting gracefully.")
            break

# ─────────────────────────────────────
# MAIN
# ─────────────────────────────────────

try:
    login_to_linkedin()
    navigate_to_section(choice)
    if choice == '2':
        time.sleep(5)
    infinite_scraping()

finally:
    driver.quit()
    csv_file.close()
    print(f"[DONE] Data saved to {csv_filename}")
