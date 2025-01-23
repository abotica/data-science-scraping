import requests
from bs4 import BeautifulSoup
import asyncio
import os
import asyncpg


URL = "https://ultragros.hr/robne-marke"
categories = []
categories_urls = []

r = requests.get(URL)
soup = BeautifulSoup(r.content, 'lxml')

table = soup.find("div", attrs={"id": "filtracija"})
link_div = table.find_all("div", class_='col col_4 kvadrat border-radius')
for div in link_div:
    link = div.find("a").get('href')

    page = requests.get(f'{link}')
    page_parse = BeautifulSoup(page.content, 'lxml')
    page_body = page_parse.find("div", attrs={"id": "filtracija-detalji"})
    
                         
                                         


