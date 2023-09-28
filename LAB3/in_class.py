import requests
from bs4 import BeautifulSoup
import re

base = "https://999.md"
start_page = 1  
max_pages = 5
page = f"https://999.md/ro/list/transport/cars"

def scrape_page(url, max_pages, current_page, urls):
    url_list = set()  
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        type = r"/ro/\d+"
        for link in links:
            href = link.get('href')
            if href:
                absolute_url = base + href
                if "booster" not in absolute_url.lower() and re.search(type, absolute_url):
                    url_list.add(absolute_url)

    else:
        print("Failed")

    if current_page < max_pages:
        n = current_page + 1
        next = page + f"?page={n}"
        print(f"page {n}: {next}")
        url_list.update(scrape_page(next, max_pages, n, urls))

    return url_list

if __name__ == "__main__":
    urls = set()
    print(f"Scraping \npage {start_page}: {page}")
    urls=scrape_page(page, max_pages, start_page, urls)
    for i in urls:
        print(i)

    with open("links.txt", "w") as file:
        for link in urls:
            file.write(link + "\n")