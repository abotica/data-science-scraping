from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()

def scroll_to_bottom():
    driver.find_element(By.TAG_NAME, 'main')

    scroll_iterations = 5
    
    for _ in range(scroll_iterations):
        ActionChains(driver).send_keys(Keys.END).perform()
        time.sleep(5)
        all_products = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='ItemCard']")
        if all_products:
            print(f"Found {len(all_products)} products")
            for product_div in all_products:
                    name_div = product_div.find_element(By.CSS_SELECTOR, "[data-test-id='ImageCentricProductCard.Title']")
                    if name_div:
                        print(name_div.text)
                    else:
                        print("Product name not found.")
            else:
                print("No products found.")
    
    print("Finished scrolling")

WOLT_URL = "https://wolt.com"
categories = []
categories_links = []
categories_urls = []

# Use requests to get the initial page content
r = requests.get("https://wolt.com/hr/hrv/split/venue/studenac-kralja-zvonimira-t300")
soup = BeautifulSoup(r.content, 'lxml')

subMenu = soup.find("div", attrs={"data-test-id": "navigation-bar"})
categories_aTag = subMenu.find_all("a", attrs={"data-test-id": "navigation-bar-link"})

for catergory_aTag in categories_aTag:
    categories_links.append(catergory_aTag['href'])

for links in categories_links:
    categories_urls.append(WOLT_URL + links)

filtered_categories_urls = [url for url in categories_urls if "https://wolt.com/hr/hrv/split/venue/studenac-kralja-zvonimira-t300/items/" in url]

for category_url in filtered_categories_urls:
    print(f"Processing URL: {category_url}")
    driver.get(category_url)
    
    # Wait for the page to load
    time.sleep(5)

    # Handle cookie consent banner if present
    try:
        consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.deorxlo button.cbc_TextButton_rootCss_7cfd4"))
        )
        consent_button.click()
        time.sleep(2)  # Wait for the cookie consent to be processed
        print("Clicked consent button.")
    except Exception as e:
        print(f"Consent button not found or not clickable: {e}")

    # Scroll down the page in smaller increments to load all products
    
    scroll_to_bottom()


    

driver.quit()