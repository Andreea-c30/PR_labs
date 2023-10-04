import socket
from bs4 import BeautifulSoup
import json

HOST = '127.0.0.1'
PORT = 8080

def send_request(path):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((HOST, PORT))

    request = f"GET {path} HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n\r\n"
    client_socket.send(request.encode('utf-8'))
    response = b""
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        response += data
    client_socket.close()
    return response.decode('utf-8')

def parse_product_page(url):
    soup = BeautifulSoup(url, 'html.parser')
    #print(soup)
    product = {}
    prod_details = soup.find('li')

    product["name"] = prod_details.find('b').text.strip()

    description = prod_details.find('p', class_='description').text.strip()
    product["description"] = description.replace("Description:", "").strip()

    author = prod_details.find('p', class_='author').text.strip()
    product["author"] = author.replace("Author:", "").strip()

    price = prod_details.find('p', class_='price').text.strip()
    product["price"] = float(price.replace("Price:", "").strip())

    return product

def listing_routes(url):
    soup = BeautifulSoup(url, 'html.parser')
    #print(soup)
    routes = []
    links = soup.find_all('a', href=True)
    for i in links:
        href = i['href']
        if '/products/' in href:
            routes.append(href)

    return routes


home = send_request("/")
print(home)
about = send_request("/about")
print(about)
contacts = send_request("/contacts")
print(contacts)
products = send_request("/products")
print(products)

with open("home.txt", "w") as file:
    file.write(home)

with open("about.txt", "w") as file:
    file.write(about)

with open("contacts.txt", "w") as file:
    file.write(contacts)

with open("products.txt", "w") as file:
    file.write(products)

prod_routes = listing_routes(products)
#print("routes: ", product_routes)
prod_details = {}

for route in prod_routes:
    prod_route = route.replace('http://127.0.0.1:8080', '')
    #print(prod_route)
    product_page = send_request(prod_route)
    #print(f"product page: {prod_route}")
    product = parse_product_page(product_page)
    # print("product", product)
    prod_details[route] = product

with open("product_details.txt", "w") as file:
    for url,item in prod_details.items():
        data = json.dumps(item, indent=4)
        print(data)
        file.write(data + "\n")





