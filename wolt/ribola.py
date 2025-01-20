from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_products(url):
    # Initialize the Selenium WebDriver
    driver = webdriver.Chrome()
    driver.get(url)
    product_list = []
    previous_length = 0

    print(f'Wep page: {url}')
    try:
        # Handle cookie consent if present
        consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.deorxlo button.cbc_TextButton_rootCss_7cfd4"))
        )
        consent_button.click()
        time.sleep(1.5)  # Wait for the cookie consent to be processed
        # print("Clicked consent button.")
    except Exception as e:
        print(f"Consent button not found or not clickable: {e}")

    while True:
        initial_html = driver.page_source
        names_h3 = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='ImageCentricProductCard.Title']")
        seen_products = set([product[0] for product in product_list])
        for name_div in names_h3:
            name = name_div.text.strip()
            if name not in seen_products:
                try:
                    price_div = driver.find_element(By.XPATH, f'//h3[contains(normalize-space(text()), "{name.replace("'", "\'")}")]/../preceding-sibling::div[1]/span')
                    price = price_div.text.strip()
                except Exception as e:
                    price = "Price not found"
                product_list.append((name, price))
                seen_products.add(name)  # Add to the set
                
            # else:
                # print(f"Skipped duplicate: {name}")
        
        # Find and scroll to the last product element
        if product_list:
            last_product_name = product_list[-1][0].strip().replace("'", "\'")
            element = driver.find_element(By.XPATH, f'//h3[contains(normalize-space(text()), "{last_product_name}")]')
            driver.execute_script("arguments[0].scrollIntoView({ block: 'start', inline: 'nearest'});", element)
            time.sleep(1.5)
        else:
            print("No products found.")
            break

        # Check if new products were loaded
        if len(product_list) == previous_length:
            break
        previous_length = len(product_list)
    
    print(f'Broj proizvoda: {len(product_list)}')
    print(product_list)
    # for product, price in product_list:
    #     print(f"{product} - {price}")
        
    driver.quit()

    print("\n")
# Main execution starts here
WOLT_URL = "https://wolt.com"
URL = "https://wolt.com/hr/hrv/split/venue/ribola-supermarket-suidar"
categories = []
categories_links = []
categories_urls = []

# Use requests to get the initial page content
r = requests.get("https://wolt.com/hr/hrv/split/venue/ribola-supermarket-suidar")
soup = BeautifulSoup(r.content, 'lxml')

subMenu = soup.find("div", attrs={"data-test-id": "navigation-bar"})
categories_aTag = subMenu.find_all("a", attrs={"data-test-id": "navigation-bar-link"})

for category_aTag in categories_aTag:
    categories_links.append(category_aTag['href'])

for links in categories_links:
    categories_urls.append(WOLT_URL + links)

filtered_categories_urls = [url for url in categories_urls if "https://wolt.com/hr/hrv/split/venue/ribola-supermarket-suidar/items/" in url]

# Scrape products for each filtered category URL
for category_url in filtered_categories_urls:
    scrape_products(category_url)
