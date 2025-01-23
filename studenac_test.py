from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get("https://wolt.com/hr/hrv/split/venue/studenac-kralja-zvonimira-t300")
time.sleep(6)

try:
    # Wait for the consent popup to be present
    consent_popup = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.cb-elevated.cb_elevation_elevationLarge_eg61"))
    )
    print("Consent popup found.")
except Exception as e:
    print(f"Consent popup not found: {e}")

time.sleep(3)

try:
    # Wait for the consent button to be clickable and click it
    consent_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.deorxlo button.cbc_TextButton_rootCss_7cfd4"))
    )
    consent_button.click()
    print("Clicked the consent button.")
except Exception as e:
    print(f"Consent button not found or not clickable: {e}")


time.sleep(10)  # Wait for a while to observe the result

driver.quit()