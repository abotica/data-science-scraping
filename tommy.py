import requests
from bs4 import BeautifulSoup
from os.path import basename

URL = "https://www.konzum.hr"
categories = []
categories_links = []
categories_urls = []

r = requests.get(URL)

soup = BeautifulSoup(r.content, 'html5lib')

table = soup.find("section", attrs={"class": "py-3"})

categories = table.find_all("a", attrs={"class": "category-box__link"})

for category in categories:
    categories_links.append(category['href'])


for links in categories_links:
    categories_urls.append(URL + links)

print(categories_urls)