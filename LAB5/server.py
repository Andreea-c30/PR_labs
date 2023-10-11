import socket
import threading
import json
import os

# Server configuration
HOST = '127.0.0.1'
PORT = 12345

clients = {}
rooms = {}

def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")

    # Receive the "connect" message from the client
    connect_message = client_socket.recv(1024).decode('utf-8')
    connect_data = json.loads(connect_message)
    if connect_data["type"] == "connect":
        name = connect_data["payload"]["name"]
        room_name = connect_data["payload"]["room"]
        print(f"{name} connected to '{room_name}'")

        # Add the client to the room
        if room_name not in rooms:
            rooms[room_name] = []
        rooms[room_name].append(client_socket)

        welcome_message = f"Hi, {name}, you joined room {room_name}"
        send_message(client_socket, "connected", {"message": welcome_message})
        send_message(client_socket, "connect_ack", {"message": "connected"})
        notification_message = f"{name} has joined the room."
        sent_notification(client_socket, room_name, notification_message)
    else:
        return

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
        except:
            break

        message_data = json.loads(message)
        if message_data["type"] == "message":
            sender = message_data["payload"]["sender"]
            room = message_data["payload"]["room"]
            chat_message = message_data["payload"]["text"]
            print(f"Received from {name} in room '{room}', message: {chat_message}")

            for client in rooms.get(room, []):
                if client != client_socket:
                    send_message(client, "message", {"sender": sender, "room": room, "message": chat_message})
        elif message_data["type"] == "upload":
            file_name = message_data["payload"]["file_name"]
            file_size = message_data["payload"]["file_size"]
            print(f"User {name} uploaded {file_name} file")

            #receive and save the uploaded file into SERVER_MEDIA folder
            file_path = os.path.join("SERVER_MEDIA", file_name)
            with open(file_path, 'wb') as file:
                content = 0
                while content < file_size:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)
                    content += len(data)
                print(f"Received file {file_name}")
            send_message(client_socket, "upload_ack", {"file_name": file_name})
        elif message_data["type"] == "download":
            file_name = message_data["payload"]["file_name"]
            file_path = os.path.join("SERVER_MEDIA", file_name)

            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                send_message(client_socket, "download_ack", {"file_name": file_name, "file_size": file_size})
        
                with open(file_path, 'rb') as file:
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        client_socket.send(data)
            else:
                send_message(client_socket, "download_error", {"message": f"The {file_name} doesn't exist"})

        elif message_data["type"] == "upload_image":
            image_name = message_data["payload"]["image_name"]
            image_size = message_data["payload"]["image_size"]
            print(f"User {name} uploaded image {image_name}")

            image_path = os.path.join("SERVER_MEDIA", image_name)
            with open(image_path, 'wb') as image:
                content = 0
                while content < image_size:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    image.write(data)
                    content += len(data)
                print(f"Received the image {image_name}")

            send_message(client_socket, "upload_image_ack", {"image_name": image_name})

        elif message_data["type"] == "download_image":
            image_name = message_data["payload"]["image_name"]
            image_path = os.path.join("SERVER_MEDIA", image_name)

            if os.path.exists(image_path):
                image_size = os.path.getsize(image_path)
                send_message(client_socket, "download_image_ack", {"image_name": image_name, "image_size": image_size})

                with open(image_path, 'rb') as image:
                    while True:
                        data = image.read(1024)
                        if not data:
                            break
                        client_socket.send(data)
            else:
                send_message(client_socket, "download_error", {"message": f"The {image_name} doesn't exist"})

        else:
            print("")

    if room_name in rooms:
        rooms[room_name].remove(client_socket)
    clients.pop(client_socket, None)
    client_socket.close()

def send_message(client_socket, message_type, payload):
    message = json.dumps({"type": message_type, "payload": payload})
    client_socket.send(message.encode('utf-8'))

def sent_notification(sender_socket, room, msg):
    for client in rooms.get(room, []):
        if client != sender_socket:
            send_message(client, "notification", {"message": msg})

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    clients[client_socket] = client_address

    # Start a new thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
