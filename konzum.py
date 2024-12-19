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



URL = "https://www.konzum.hr"
categories = []
categories_links = []
categories_urls = []

r = requests.get(URL)

soup = BeautifulSoup(r.content, 'lxml')

table = soup.find("section", attrs={"class": "py-3"})

categories = table.find_all("a", attrs={"class": "category-box__link"})

for category in categories:
    categories_links.append(category['href'])


for links in categories_links:
    categories_urls.append(URL + links)

# print(categories_urls)

for category_url in categories_urls:
    page = requests.get(f'{category_url}').text
    pageSoup = BeautifulSoup(page, 'lxml')

    subCategories = pageSoup.find('ul', class_='plain-list mb-3')
    subCategories_aTag = subCategories.find_all('a')
    
    if subCategories_aTag:
        for aTag in subCategories_aTag:
            subCategoryLink = aTag.get('href')
            subCategoryURL = URL + subCategoryLink
             
            if subCategoryURL:
                    page_number = 1
                    count = 0
                    while True:
                        finalPage = requests.get(f'{subCategoryURL}?page={page_number}')
                        # print(f'{subCategoryURL}?page={page_number}')
                        if finalPage.status_code != 200:
                            print(f"Page {page_number} does not exist. Exiting pagination.")
                            break
                        finalSoup = BeautifulSoup(finalPage.text, 'lxml')
                        allItems = finalSoup.find('div', class_ = 'col-12 col-md-12 col-lg-10')
                        if not allItems:
                            break

                        productsList = allItems.find('div', class_='product-list product-list--md-5 js-product-layout-container product-list--grid')
                        if not productsList:
                            break

                        articles = productsList.find_all('article', class_='product-item product-default')
                        if not articles:
                            break

                        for article in articles:
                            articleImageURL = article.find('img').get('src')

                            if articleImageURL:
                                articleTittleTag = article.find('h4', class_ ='product-default__title')
                                if articleTittleTag:
                                    articleNameTag = articleTittleTag.find('a', class_='link-to-product')
                                    if articleNameTag:
                                        articleName = articleNameTag.get_text(strip=True)
                                        if articleName:
                                            articleEuro = article.find('span', class_='price--kn').text
                                            articleCent = article.find('span', class_='price--li').text
                                            articleCurrency = article.find('small', class_='price--c').text
                                            asyncio.run(insert(articleName, float(f'{articleEuro}.{articleCent}'), articleImageURL, 'Konzum'))
                                            count+=1
                        page_number+=1
                         
                                         


