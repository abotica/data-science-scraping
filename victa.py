import requests
from bs4 import BeautifulSoup
import asyncio
import os
import asyncpg
from dotenv import load_dotenv

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



URL = "https://ultragros.hr/robne-marke"
categories = []
categories_urls = []

r = requests.get(URL)

soup = BeautifulSoup(r.content, 'lxml')

table = soup.find("div", attrs={"id": "filtracija"})

categories = table.find_all("a")

for category in categories:
    categories_urls.append(category['href'])

for category_url in categories_urls:
    page = requests.get(category_url).text
    pageSoup = BeautifulSoup(page, 'lxml')

             
    count = 0
    while True:

        allItems = pageSoup.find('div', id='filtracija-detalji')
        if not allItems:
            break
        anchors = allItems.findAll('a')
        if not anchors:
            break
        for anchor in anchors:
            anchor_page = requests.get(anchor['href']).text
            anchor_soup = BeautifulSoup(anchor_page, 'lxml')
            print(anchor_soup)
            anchor_div = anchor_soup.find('div', class_="col col_6 slika-prozvoda pro-height")
            anchor_image = anchor_div.find('img')
            
            anchor_image_src = anchor_image['src']
            # print(anchor_image_src)
            
            # if anchor_image:
            #     articleTittleTag = anchor.find('h3', class_ ='mb-2 text-sm pr-2 font-normal text-gray-900 line-clamp-2 hover:underline cursor-pointer')
            #     articleName = articleTittleTag.text
            #     if articleTittleTag:        
            #         articlePrice = anchor.find('span', class_='mt-auto inline-block-block text-sm font-bold text-gray-900').text
            #         articlePrice = articlePrice[:-2]
            #         priceSplit = articlePrice.split(',')
            #         priceEuro = priceSplit[0]
            #         priceCent = priceSplit[1]
            #         articlePrice = float(f'{priceEuro}.{priceCent}')
            #         print(articleName, articlePrice, anchor_image, 'Tommy')
            #         # asyncio.run(insert(articleTittleTag, float(articlePrice), anchor_image, 'Tommy'))
            #         count+=1
        
                         
                                         


