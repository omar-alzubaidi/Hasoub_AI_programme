import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up undetected Chrome
options = uc.ChromeOptions()
# options.headless = True  # Optional: run headless
driver = uc.Chrome(options=options)

# Open Google
driver.get('https://www.google.com/ncr')

# Wait until search box is ready
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'q'))
    )
    element.clear()
    element.send_keys('Hsoub Academy')
    element.send_keys(Keys.RETURN)

    print("✅ Search completed successfully on Google!")
    time.sleep(5)  # Let the page load
except Exception as e:
    print(f"❌ Error happened: {e}")

driver.quit()
