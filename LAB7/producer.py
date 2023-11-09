import requests
from bs4 import BeautifulSoup
import pika

base = 'https://999.md'
url = "https://999.md/ro/list/musical-instruments/strings"
data = []
unique_urls = set()
def scaraper(current_link, data, unique_urls):
    response = requests.get(current_link)
    soup = BeautifulSoup(response.content, "html.parser")

    for link in soup.find_all('a', class_='js-item-ad'):
        link = link.get('href')
        if "booster" not in link:
            url = base + link
            if url not in unique_urls:
                data.append(url)
                unique_urls.add(url)

    max_pages = soup.select('nav.paginator > ul > li > a')
    for page in max_pages:
        link = str(base + page['href'])
        if link not in unique_urls:
            unique_urls.add(link)
            scaraper(link, data, unique_urls)



if __name__ == "__main__":
    # establish a connection to the RabbitMQ server
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    #declare the queue
    queue_name = 'newqueue'
    channel.queue_declare(queue=queue_name)
    scaraper(url, data, unique_urls)

    f = open("links.txt", "w")
    # publish links to the queue
    for link in data:
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=link,
                              properties=pika.BasicProperties(
                                  delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                              ))
        print(f"[x] Sent {link}")
        f.write(link + "\n")
    f.close()
    connection.close()
