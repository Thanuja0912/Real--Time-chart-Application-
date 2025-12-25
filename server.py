import socket
import threading
from datetime import datetime

HOST = '127.0.0.1'
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}  # socket : nickname

print("🔥 Chat Server Started...")

def broadcast(message, sender=None):
    for client in clients:
        if client != sender:
            client.send(message)

def private_message(sender, target_nick, message):
    for client, nickname in clients.items():
        if nickname == target_nick:
            client.send(message)
            return True
    return False

def handle_client(client):
    nickname = clients[client]
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            time = datetime.now().strftime("%H:%M")

            # Exit command
            if msg == "/exit":
                raise Exception

            # List users
            elif msg == "/users":
                users = ", ".join(clients.values())
                client.send(f"Online Users: {users}".encode('utf-8'))

            # Private message
            elif msg.startswith("/pm"):
                _, target, private_msg = msg.split(" ", 2)
                success = private_message(
                    client,
                    target,
                    f"[{time}] [PM] {nickname}: {private_msg}".encode('utf-8')
                )
                if not success:
                    client.send("User not found!".encode('utf-8'))

            # Normal message
            else:
                broadcast(
                    f"[{time}] {nickname}: {msg}".encode('utf-8'),
                    sender=client
                )

        except:
            print(f"{nickname} disconnected")
            broadcast(f"{nickname} left the chat!".encode('utf-8'))
            del clients[client]
            client.close()
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected: {address}")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        clients[client] = nickname
        print(f"Nickname: {nickname}")

        broadcast(f"{nickname} joined the chat!".encode('utf-8'))
        client.send("Connected successfully!".encode('utf-8'))

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

receive()
