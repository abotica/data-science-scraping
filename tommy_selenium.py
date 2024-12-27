from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time

import requests
from bs4 import BeautifulSoup
import asyncio
import os
import asyncpg
from dotenv import load_dotenv


# Database insertion function
async def insert(name, price, image_url, store_name):
    # Load .env file
    load_dotenv()
    connection_string = os.getenv('DATABASE_URL')
    pool = await asyncpg.create_pool(connection_string)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO products (name, price, image_url, store_name)
            VALUES ($1, $2, $3, $4);
            """,
            name, price, image_url, store_name
        )
        table = await conn.fetch('SELECT * FROM products;')
    await pool.close()
    print(table)

# Initialize Selenium WebDriver
driver = webdriver.Chrome()

# BeautifulSoup init
URL = "https://www.tommy.hr"
r = requests.get(URL)
soup = BeautifulSoup(r.content, 'lxml')

# Find category links
categories_container = soup.find("div", attrs={"class": "@container/categories"})
categories = categories_container.find_all("a")
categories_urls = [URL + category['href'] for category in categories]

# Process each category
for category_url in categories_urls:
    driver.get(category_url)
    page_number = 1

    while True:
        # Wait for the page to load and ensure products are visible
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="@container flex  flex-wrap -mx-1 xs:-mx-2.5"]'))
            )
        except Exception as e:
            print(f"Timeout waiting for products on {category_url}: {e}")
            break

        # Parse the page with BeautifulSoup
        page_soup = BeautifulSoup(driver.page_source, 'lxml')
        all_items = page_soup.find('div', class_='@container flex flex-wrap -mx-1 xs:-mx-2.5')
        if not all_items:
            print(f"No items found on page {page_number} of {category_url}")
            break

        # Extract product data
        articles = all_items.find_all('article')
        if not articles:
            break

        for article in articles:
            # Extract product details
            image_element = article.find('img')
            if not image_element:
                continue

            # Handle dynamic image loading
            try:
                image_element_web = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//img[@src="{image_element["src"]}"]'))
                )
                actual_image_url = image_element_web.get_attribute('src')
                print(actual_image_url)
            except Exception as e:
                print(f"Error loading image for article: {e}")
                continue

            title_tag = article.find('h3', class_='mb-2 text-sm pr-2 font-normal text-gray-900 line-clamp-2 hover:underline cursor-pointer')
            if not title_tag:
                continue
            article_name = title_tag.text.strip()

            price_tag = article.find('span', class_='mt-auto inline-block-block text-sm font-bold text-gray-900')
            if not price_tag:
                continue
            article_price_raw = price_tag.text.strip()[:-2]
            price_split = article_price_raw.split(',')
            article_price = float(f"{price_split[0]}.{price_split[1]}")

            # Insert into database
            # asyncio.run(insert(article_name, article_price, actual_image_url, 'Tommy'))

        # Move to the next page
        page_number += 1
        next_page_url = f"{category_url}?page={page_number}"
        driver.get(next_page_url)

driver.quit()