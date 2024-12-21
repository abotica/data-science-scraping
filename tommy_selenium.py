from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
import asyncio
import os
import asyncpg
from dotenv import load_dotenv


# database insertion function
async def insert(name, price, image_url, store_name):
    # Load .env file
    load_dotenv()
    # Get the connection string from the environment variable
    connection_string = os.getenv('DATABASE_URL')
    # Create a connection pool
    pool = await asyncpg.create_pool(connection_string)
    # Acquire a connection from the pool
    async with pool.acquire() as conn:
        # Execute SQL commands to retrieve the current time and version from PostgreSQL
        # time = await conn.fetchval('SELECT NOW();')
        # version = await conn.fetchval('SELECT version();')
        # Insert data into the table
        await conn.execute(
            """
            INSERT INTO products (name, price, image_url, store_name)
            VALUES ($1, $2, $3, $4);
            """,
            name, price, image_url, store_name
        )
        
        # Retrieve data from the table to verify insertion
        table = await conn.fetch('SELECT * FROM products;')
    # Close the pool
    await pool.close()
    # Print the results
    print(table)


# beautifulsoup init
URL = "https://www.tommy.hr"
categories = []
categories_links = []
categories_urls = []

# selenium init
driver = webdriver.Chrome()

r = requests.get(URL)

soup = BeautifulSoup(r.content, 'lxml')

table = soup.find("div", attrs={"class": "@container/categories"})

categories = table.find_all("a")

for category in categories:
    categories_links.append(category['href'])

for links in categories_links:
    categories_urls.append(URL + links)


for category_url in categories_urls:
    page = requests.get(f'{category_url}').text
    pageSoup = BeautifulSoup(page, 'lxml')

    driver.get(category_url)
             
    page_number = 1
    count = 0
    while True:
        finalPage = requests.get(f'{category_url}?page={page_number}')
        # print(f'{category_url}?page={page_number}')
        if finalPage.status_code != 200:
            # print(f"Page {page_number} does not exist. Exiting pagination.")
            break
        finalSoup = BeautifulSoup(finalPage.text, 'lxml')
        allItems = finalSoup.find('div', class_ ='@container flex flex-wrap -mx-1 xs:-mx-2.5')
        if not allItems:
            break
        articles = allItems.findAll('article')
        if not articles:
            break
        for article in articles:
            articleImageURL = article.find('img')['src']
            
            image_src = driver.find_element(By.CSS_SELECTOR, f'img[src="{articleImageURL}"]')
            
            
            print(image_src.get_attribute('src'))

             
            articleImageURL = URL + articleImageURL
            if articleImageURL:
                articleTittleTag = article.find('h3', class_ ='mb-2 text-sm pr-2 font-normal text-gray-900 line-clamp-2 hover:underline cursor-pointer')
                articleName = articleTittleTag.text
                if articleTittleTag:        
                    articlePrice = article.find('span', class_='mt-auto inline-block-block text-sm font-bold text-gray-900').text
                    articlePrice = articlePrice[:-2]
                    priceSplit = articlePrice.split(',')
                    priceEuro = priceSplit[0]
                    priceCent = priceSplit[1]
                    articlePrice = float(f'{priceEuro}.{priceCent}')
                    # print(articleName, articlePrice, articleImageURL, 'Tommy')
                    # asyncio.run(insert(articleTittleTag, float(articlePrice), articleImageURL, 'Tommy'))
                    count+=1
        page_number+=1
                         
                                         


driver.quit()