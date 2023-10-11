import socket
import threading
import json
import os

# Server configuration
HOST = '127.0.0.1'
PORT = 12345

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")


def receive_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        message_data = json.loads(message)
        if message_data["type"] == "connected":
            print(message_data["payload"]["message"])
        elif message_data["type"] == "message":
            sender = message_data["payload"]["sender"]
            room = message_data["payload"]["room"]
            text = message_data["payload"]["message"]
            print(f"{sender} in room '{room}': {text}")
        elif message_data["type"] == "error":
            err = message_data["payload"]["message"]
            print(err)
        elif message_data["type"] == "connect_ack":
            ack_message = message_data["payload"]["message"]
            print(f"Connection: {ack_message}")
        #handle uploads of files
        elif message_data["type"] == "upload_ack":
            file_name = message_data["payload"]["file_name"]
            print(f"File '{file_name}' uploaded successfully.")
        # handle uploads of images
        elif message_data["type"] == "upload_image_ack":
            image_name = message_data["payload"]["image_name"]
            print(f"Image '{image_name}' uploaded successfully.")
        # handle file downloads
        elif message_data["type"] == "download_ack":
            name = message_data["payload"]["file_name"]
            size = message_data["payload"]["file_size"]
            print(f"Downloading file: {name}")
            save_folder = os.path.join("downloads", name)
            #download the file from server and save it in downloads folder
            with open(save_folder, 'w', encoding='utf-8') as file:
                content = 0
                while content < size:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    file.write(data)
                    content += len(data)
                print(f"File {name} was downloaded")
        # handle img downloads
        elif message_data["type"] == "download_image_ack":
            name = message_data["payload"]["image_name"]
            size = message_data["payload"]["image_size"]
            print(f"Downloading image: {name}")
            save_folder = os.path.join("downloads", name)
            # get and save the image as binary data
            with open(save_folder, 'wb') as image:
                content = 0
                while content < size:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    image.write(data)
                    content += len(data)
                print(f"Image {name} was downloaded")

        elif message_data["type"] == "download_error":
            err = message_data["payload"]["message"]
            print(err)
        else:
            print("")


receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

client_name = input("Name: ")
room_name = input("Room: ")
connect_message = json.dumps({"type": "connect", "payload": {"name": client_name, "room": room_name}})
client_socket.send(connect_message.encode('utf-8'))

while True:
    message = input("Enter a message ('exit'-quit, 'upload'/'download'/'upload_image'/'download_image' a file/image):")

    if message.lower() == 'exit':
        print("User exited from the room")
        break
    # uploading files txt
    elif message.lower() == 'upload':
        path = input("file path: ")
        name = os.path.basename(path)
        if os.path.exists(path):
            size = os.path.getsize(path)
            file_data = json.dumps({
                "type": "upload",
                "payload": {"file_name": name,
                            "file_size": size}
            })
            client_socket.send(file_data.encode('utf-8'))
            with open(path, 'r', encoding='utf-8') as file:
                data = file.read()
                client_socket.send(data.encode('utf-8'))
        else:
            print(f"File {name} doesnt exist")

    # downloading files
    elif message.lower().startswith('download'):
        words = message.split(' ')
        if len(words) >= 2:
            name = words[1]
            if message.lower().startswith('download_image'):
                content_data = json.dumps({
                    "type": "download_image",
                    "payload": {"image_name": name}
                })
            else:
                content_data = json.dumps({
                    "type": "download",
                    "payload": {"file_name": name}
                })
            client_socket.send(content_data.encode('utf-8'))
        else:
            print(" Error ")

    # uploading image
    elif message.lower() == 'upload_image':
        path = input("Input path: ")
        name = os.path.basename(path)
        if os.path.exists(path):
            size = os.path.getsize(path)
            img_content = json.dumps({
                "type": "upload_image",
                "payload": {
                    "image_name": name,
                    "image_size": size
                }
            })
            client_socket.send(img_content.encode('utf-8'))
            with open(path, 'rb') as image:
                while True:
                    data = image.read(1024)
                    if not data:
                        break
                    client_socket.send(data)
        else:
            print(f"Image {name} doesnt exist")

    else:
        text = json.dumps({"type": "message",
                           "payload": {"sender": client_name,
                                       "room": room_name,
                                       "text": message}})
        client_socket.send(text.encode('utf-8'))

# Close the client socket when done
client_socket.close()
