from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
import re


def scrape_products(url, cat_name):

    driver = webdriver.Chrome()
    driver.get(url)
    product_list = []
    previous_length = 0
    visited_pages = set()

    print(f'Wep page: {url}')
    try:
        consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.deorxlo button.cbc_TextButton_rootCss_7cfd4"))
        )
        consent_button.click()
        time.sleep(1)
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
                    if price_div:
                        image_url = price_div.find_element(By.XPATH, "./../../preceding-sibling::div[1]/span/img").get_attribute('src')
                    else:
                        image_url = ""
                except Exception as e:
                    price = "Price not found"
                product_list.append((name, price, image_url))
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

        try:
            pagination = driver.find_elements(By.CSS_SELECTOR, "li.text-center.text-gray-100.text-sm.cursor-pointer a") 
            for page in pagination:
                page_number = page.text.strip()
                if page_number not in visited_pages:
                    print(f"Clicking on page number: {page_number}")
                    visited_pages.add(page_number)
                    page.click()
                    time.sleep(2)  # Wait for the next page to load
                    break  # Break after clicking the next page to avoid clicking multiple pages at once
        except Exception as e:
            print(f"No more pages: {e}")
            break

    
    print(f'Broj proizvoda: {len(product_list)}')
    print(product_list)
    # for product, price in product_list:
    #     print(f"{product} - {price}")
        
    driver.quit()

    print("\n")

    # Create a pandas DataFrame from the product list
    df = pd.DataFrame(product_list, columns=['Product Name', 'Price', 'ImageURL']) 
    df['PageURL'] = url
    df['Category'] = cat_name
    df = df[['Product Name', 'Price', 'Category', 'ImageURL', 'PageURL']]

    # Save the DataFrame to a CSV file, appending if the file exists
    file_exists = os.path.isfile('studenac.csv')
    df.to_csv('studenac.csv', mode='a', header=not file_exists, index=False)

    
# Main execution starts here
WOLT_URL = "https://wolt.com/hr/hrv/split/venue/studenac-kralja-zvonimira-t300/items/"
URL = "https://wolt.com/hr/hrv/split/venue/studenac-kralja-zvonimira-t300"
categories = []
categories_links = []
categories_urls = []

driver = webdriver.Chrome()
driver.get(URL)

try:
    consent_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.deorxlo button.cbc_TextButton_rootCss_7cfd4"))
    )
    consent_button.click()
    time.sleep(1)
except Exception as e:
    print(f"Consent button not found or not clickable: {e}")

try:
    x_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class='cbc_IconButton_root_7cfd4 c1hmjr97']"))
    )
    x_button.click()
    time.sleep(1) 
except Exception as e:
    print(f"X button not found or not clickable: {e}")


subMenu = driver.find_element(By.CSS_SELECTOR, "div[data-test-id='navigation-bar']")
head_nav_aTag = driver.find_elements(By.CSS_SELECTOR, "a[data-test-id='navigation-bar-link']")
if head_nav_aTag:
    for head_nav in head_nav_aTag:
        categories_links.append(head_nav.get_attribute('href'))

filtered_categories_urls = [url for url in categories_links if "https://wolt.com/hr/hrv/split/venue/studenac-kralja-zvonimira-t300/items/" in url]

if filtered_categories_urls:
    for filtered_category_url in filtered_categories_urls:
        page_url = filtered_category_url.replace("https://wolt.com", "")
        a_Tag = driver.find_element(By.XPATH, f'//a[contains(@href, "{page_url}")]')
        a_Tag_parent = a_Tag.find_element(By.XPATH, "./ancestor::div[1]")
        a_Tag.click()
        time.sleep(1)
        temporary = a_Tag_parent.find_element(By.XPATH, "./ancestor::div[1]")
        if 'a1qapeeb rljt8w0' in temporary.get_attribute('class'):
            subpage_divs = a_Tag_parent.find_elements(By.XPATH, "./following-sibling::div[1]//a[@data-test-id='navigation-bar-link']")
            if subpage_divs:
                for subpage_div in subpage_divs:
                    subpage_url = subpage_div.get_attribute('href')
                    subcategory_name = subpage_div.find_element(By.XPATH, "./div[@data-test-id='NavigationListItem-title']")
                    scrape_products(subpage_url, subcategory_name.text)
            else:
                print("Error with getting a tags")
        else:
            category_name =  a_Tag.find_element(By.XPATH, "./div[@data-test-id='NavigationListItem-title']")
            scrape_products(filtered_category_url, category_name.text)
            print("Else")

        driver.execute_script("arguments[0].scrollIntoView({ block: 'start', inline: 'nearest'});", a_Tag_parent)
        time.sleep(1)
   