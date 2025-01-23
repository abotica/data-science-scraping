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

def kromanjonac(url, cat_name, product_list):
    driver = webdriver.Chrome()
    driver.get(url)
    previous_length = len(product_list)
    # print(f'New page: previous length = {previous_length}')
    # print(f'Product_list: {product_list}')

    while True:
        all_products_container = driver.find_element(By.CSS_SELECTOR, "div[class='@container flex  flex-wrap -mx-1 xs:-mx-2.5 ']")
        if all_products_container:
            products_container = all_products_container.find_elements(By.XPATH, "article")
            print(f'Number of products found: {len(products_container)}')
            seen_products = set([product[0] for product in product_list])
            for product_container in products_container:
                name_element = product_container.find_element(By.CSS_SELECTOR, "h3.mb-2.text-sm.pr-2.font-normal.text-gray-900.line-clamp-2.hover\\:underline.cursor-pointer a")
                if name_element:
                    name = name_element.text.strip()
                    if name:
                        if name not in seen_products:
                            try:
                                price_div = product_container.find_element(By.CSS_SELECTOR, "div.w-full.h-full.flex.flex-col.my-4.leading-normal")
                                price = price_div.find_element(By.CSS_SELECTOR, "span").text.strip()
                                product_list.append((name, price))
                                seen_products.add(name)
                            except Exception as e:
                                price = "Price not found"
                                print("Price not found")
                        else:
                            print(f"Skipped duplicate: {name}")

        if product_list:
            last_product_name = product_list[-1][0].strip().replace("'", "\'")
            element = driver.find_element(By.XPATH, f'//a[contains(normalize-space(text()), "{last_product_name}")]')
            if element:
                driver.execute_script("arguments[0].scrollIntoView({ block: 'start', inline: 'nearest'});", element)
                time.sleep(1.5)
                if len(product_list) == previous_length:
                    break
                previous_length = len(product_list)
            else:
                last_article = product_container[-1]
                driver.execute_script("arguments[0].scrollIntoView({ block: 'start', inline: 'nearest'});", last_article)
                time.sleep(2)
        else:
            print("No products found.")
            break



    # print(f'New Page: After_length = {len(product_list)}')
    # print(f'After: Product list = {product_list}')

    try:
        current_li = driver.find_element(By.CSS_SELECTOR, "li.text-center.text-gray-100.text-sm.cursor-pointer.selected")
        next_li = current_li.find_element(By.XPATH, "./following-sibling::li[1]")
        next_li_classes = next_li.get_attribute("class")
        if "text-center text-gray-100 text-sm cursor-pointer" in next_li_classes:
            a_element = next_li.find_element(By.CSS_SELECTOR, "a")
            next_page_url = a_element.get_attribute('href')
            driver.quit()
            time.sleep(1)
            kromanjonac(next_page_url, cat_name, seen_products)
    except Exception as e:
        print(f"No more pages: {e}")
        print(f'Broj proizvoda: {len(product_list)}')
        print(product_list)
        driver.quit()


def scrape_products(url, cat_name):
    driver = webdriver.Chrome()
    driver.get(url)
    product_list = []
    previous_length = 0

    while True:
        all_products_container = driver.find_element(By.CSS_SELECTOR, "div[class='@container flex  flex-wrap -mx-1 xs:-mx-2.5 ']")
        if all_products_container:
            products_container = all_products_container.find_elements(By.XPATH, "article")
            # print(f'Number of products found: {len(products_container)}')
            seen_products = set([product[0] for product in product_list])
            for product_container in products_container:
                name_element = product_container.find_element(By.CSS_SELECTOR, "h3.mb-2.text-sm.pr-2.font-normal.text-gray-900.line-clamp-2.hover\\:underline.cursor-pointer a")
                name = name_element.text.strip()
                if name:
                    if name not in seen_products:
                        try:
                            price_div = product_container.find_element(By.CSS_SELECTOR, "div.w-full.h-full.flex.flex-col.my-4.leading-normal")
                            price = price_div.find_element(By.CSS_SELECTOR, "span").text.strip()
                            product_list.append((name, price))
                            seen_products.add(name)
                        except Exception as e:
                            price = "Price not found"
                            print("Price not found")
                    else:
                        print(f"Skipped duplicate: {name}")

        if product_list:
            last_product_name = product_list[-1][0].strip().replace("'", "\'")
            element = driver.find_element(By.XPATH, f'//a[contains(normalize-space(text()), "{last_product_name}")]')
            driver.execute_script("arguments[0].scrollIntoView({ block: 'start', inline: 'nearest'});", element)
            time.sleep(1.5)
        else:
            print("No products found.")
            break

        if len(product_list) == previous_length:
            break
        previous_length = len(product_list)


    try:
        current_li = driver.find_element(By.CSS_SELECTOR, "li.text-center.text-gray-100.text-sm.cursor-pointer.selected")
        # print(f'current_li = {current_li}')
        next_li = current_li.find_element(By.XPATH, "./following-sibling::li[1]")
        # print(f'next_li = {next_li}')
        next_li_classes = next_li.get_attribute("class")
        if "text-center text-gray-100 text-sm cursor-pointer" in next_li_classes:
            a_element = next_li.find_element(By.CSS_SELECTOR, "a")
            # print(f'a_element = {a_element}')
            a_number = a_element.text.strip()
            # print(f'number = {a_number}')
            next_page_url = f"{url}?page={a_number}"
            # print(f'next_page_url = {next_page_url}')
            # driver.quit()
            # time.sleep(2)
            kromanjonac(next_page_url, cat_name, product_list)
    except Exception as e:
        print(f"No more pages: {e}")
        print(f'Broj proizvoda: {len(product_list)}')
        print(product_list)
        # driver.quit()
        # time.sleep(2)

    driver.quit()
    


URL = "https://www.tommy.hr"
WANTED_HREF = "/kategorije/"
EXCLUDE_URL = "https://www.tommy.hr/kategorije/robne-marke"
categories = []
categories_links = []
categories_urls = []

driver = webdriver.Chrome()
driver.get(URL)
try:
        consent_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Prihvati samo potrebno']")))
        consent_button.click()
        time.sleep(1)
except Exception as e:
        print(f"Consent button not found or not clickable: {e}")

categories_menu = driver.find_element(By.CSS_SELECTOR, "div[class='@container flex  flex-wrap -mx-1 xs:-mx-2.5 ']")
categories_all = categories_menu.find_elements(By.XPATH, f'a[contains(@href, "{WANTED_HREF}")]')

filtered_categories_urls = [category for category in categories_all if category.get_attribute('href') != EXCLUDE_URL]
filtered_categories_urls = filtered_categories_urls[:-1]


for filtered_category in filtered_categories_urls:
    driver = webdriver.Chrome()
    driver.get(filtered_category.get_attribute('href'))
    try:
        consent_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Prihvati samo potrebno']")))
        consent_button.click()
        time.sleep(1)
    except Exception as e:
        print(f"Consent button not found or not clickable: {e}")

    subMenu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.container.mb-12.lg\\:px-10.lg\\:pt-5"))
    )
    if subMenu:
        a_Tags = subMenu.find_elements(By.CSS_SELECTOR, "li.py-4.text-sm.font-bold.text-gray-900.cursor-pointer a")
        for a in a_Tags:
            scrape_products(a.get_attribute('href'), a.text)
    else:
         print(f'{filtered_category.get_attribute('href')} has no subcategories')

driver.quit()


	