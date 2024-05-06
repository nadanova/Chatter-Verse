# Server.py
import socket
import threading
from collections import defaultdict

# Server setup
host = socket.gethostbyname(socket.gethostname())
port = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()

print(f'[LISTENING] Server is listening on {host}')

clients = []
nicknames = []
vote_kicks = defaultdict(set)
# Configurable Kick Threshold
KICK_THRESHOLD = 2


def broadcast(message, exclude_client=None):
    for client in clients:
        if client != exclude_client:
            try:
                client.send(message)
            except socket.error:
                disconnect_client(client)


def disconnect_client(client):
    if client in clients:
        index = clients.index(client)
        nickname = nicknames[index]
        clients.remove(client)
        nicknames.remove(nickname)
        broadcast(f'{nickname} left!'.encode('UTF-16'))
        client.close()


def handle_vote_kick(issuer_nickname, target_nickname):
    if target_nickname in nicknames:
        issuer_index = nicknames.index(issuer_nickname)
        target_index = nicknames.index(target_nickname)

        # Add the issuer's vote to the target's vote set
        vote_kicks[target_nickname].add(issuer_nickname)

        # Check if the number of votes is more than or equal to the threshold
        if len(vote_kicks[target_nickname]) >= KICK_THRESHOLD:
            client_to_kick = clients[target_index]
            clients.remove(client_to_kick)
            nicknames.remove(target_nickname)

            try:
                client_to_kick.send("You have been kicked out!".encode('UTF-16'))
            except socket.error:
                pass

            client_to_kick.close()
            broadcast(f'{target_nickname} has been kicked out.'.encode('UTF-16'))
            del vote_kicks[target_nickname]


def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('UTF-16')
            if message.startswith('/kick'):
                nickname_to_kick = message.split()[1]
                index = clients.index(client)
                issuer_nickname = nicknames[index]
                handle_vote_kick(issuer_nickname, nickname_to_kick)
            else:
                broadcast(message.encode('UTF-16'))
        except:
            disconnect_client(client)
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"[NEW CONNECTION] {address} connected.")

        try:
            client.send("".encode('UTF-16'))
            nickname = client.recv(1024).decode('UTF-16')
        except socket.error:
            client.close()
            continue

        nicknames.append(nickname)
        clients.append(client)

        print(f"{nickname} joined the chat!")
        broadcast(f"{nickname} joined the chat!".encode('UTF-16'))
        client.send("Connected to the server!".encode('UTF-16'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


if __name__ == "__main__":
    receive()
