import socket
import signal
import sys
import threading
from time import sleep
import json
import re
# Define the server's IP address and port
HOST = '127.0.0.1'  # IP address to bind to (localhost)
PORT = 8080  # Port to listen on

# Create a socket that uses IPv4 and TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen(5)  # Increased backlog for multiple simultaneous connections
print(f"Server is listening on {HOST}:{PORT}")

# Function to handle client requests
def products_info():
    with open('products.json', 'r') as json_file:
        products = json.load(json_file)
    return products

def print_data(id):
    products = products_info()
    product = products[id]
    response_content = ''
    response_content += f'''
                        <div class=product-details><h1>Product details</h1><li>
                          <b>{product['name']}</b>
                           <p class="description">Description: {product['description']}</p>
                          <p class="author">Author: {product['author']}</p>
                          <p class="price">Price: {product['price']}</p></li>'''
    return response_content

def handle_request(client_socket):
 # Receive and print the client's request data
 request_data = client_socket.recv(1024).decode('utf-8')
 print(f"Received Request:\n{request_data}")

 # Parse the request to get the HTTP method and path
 request_lines = request_data.split('\n')
 request_line = request_lines[0].strip().split()
 path = request_line[1]
 # Initialize the response content and status code
 response_content = ''
 status_code = 200

 # Define a simple routing mechanism
 if path == '/':
  response_content = 'Home Page'
 elif path == '/about':
  response_content = 'About'
 elif path == '/contacts':
  response_content = 'Contacts'
 elif path == '/products':
    products=products_info()
    for id in range(0,len(products)):
        response_content += f'<p><a href ="http://127.0.0.1:8080/products/{id}">Product_{id}</a></p>\n'
 elif re.match(r'^/products/(\d+)$', path):
     match = re.match(r'^/products/(\d+)$', path)
     products = products_info()
     if match:
         id = int(match.group(1))
         if id<len(products):
            response_content = print_data(id)
         else:
             response_content = '404 Not Found'
             status_code = 404
 else:
     response_content = '404 Not Found'
     status_code = 404


 # Prepare the HTTP response headers
 response_headers = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n'

 # Add Content-Length header based on the response content length
 content_length = len(response_content)
 response_headers += f'Content-Length: {content_length}\n\n'

 # Combine headers and content and send as a single response
 response = response_headers + response_content
 client_socket.send(response.encode('utf-8'))

 # Close the client socket
 client_socket.close()

# Function to handle Ctrl+C and other signals
def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

while True:
    # Accept incoming client connections
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    # Create a thread to handle the client's request
    client_handler = threading.Thread(target=handle_request, args=(client_socket,))
    client_handler.start()