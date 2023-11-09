import pika
import threading
import requests
from bs4 import BeautifulSoup
import json
from tinydb import TinyDB

# Initialize TinyDB
db = TinyDB('data.json', ensure_ascii=False, encoding='utf-8')


def retrive_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        data = {
            "title": soup.title.string,
            "descriere": " ",
            "subcategorie": "",
            "preț": "",
            "regiunea": "",
            "contacte": []
        }
        descrip = soup.find("div", class_="adPage__content__description grid_18", itemprop="description")
        if descrip:
            data["descriere"] = descrip.get_text(strip=True)
        else:
            data["descriere"] = ''

        subcat = soup.find("a", class_="adPage__content__features__category__link")
        if subcat:
            data["subcategorie"] = subcat.get_text(strip=True)
        else:
            data["subcategorie"] = ''

        pret = soup.find("ul", class_="adPage__content__price-feature__prices")
        data["preț"] = pret.get_text(strip=True)

        region = soup.find("dl", class_="adPage__content__region grid_18")
        name = region.get_text(strip=True)
        data["regiunea"] = name.replace("Regiunea:", "").strip()

        contacts = soup.find("dl", class_="js-phone-number adPage__content__phone is-hidden grid_18")
        if contacts:
            c = contacts.get_text(strip=True)
            data["contacte"] = c.replace("Contacte:", "").strip()
        else:
            data["contacte"] = ''

        info = json.dumps(data, ensure_ascii=False)

    else:
        print("Something went wrong")
    return info


def consumer(nr):
    # establish a connection to the RabbitMQ server
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    # declare the queue
    queue_name = 'newqueue'
    channel.queue_declare(queue=queue_name)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    #function to process received messages
    def callback(ch, method, properties, body):
        print(f"Thread: {nr} - Received {body}")
        json_data = retrive_data(body)
        if json_data is not None:
            try:
                data_dict = json.loads(json_data)
                db.insert(data_dict)
            except json.decoder.JSONDecodeError as e:
                pass
        else:
            print("Error retrieving data")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    # eet up the consumer with the callback()
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    # start consuming messages
    channel.start_consuming()


if __name__ == "__main__":
    thread_nr  = 4
    threads = []
    for i in range(thread_nr ):
            thread = threading.Thread(target=consumer, args=(i,))
            threads.append(thread)
            thread.start()
    # wait for threads to complete
    for thread in threads:
            thread.join()

    db.close()
