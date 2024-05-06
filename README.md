# Chatter-Verse
Chatter-Verse is a multilingual LAN chat application with a user-friendly GUI. Built using Python's socket, threading, and tkinter, it allows seamless communication between neighbours over a local network. It also supports vote-kicking capabilities. Developed with my friend, Menna Alaa Eldin.


#Features

  #Server:
  
    Accepts multiple client connections.
    Broadcasts messages to all connected clients.
    Supports vote-kicking functionality to remove disruptive clients.
  #Client:
  
    Allows users to connect to the server.
    Supports both Arabic and English input, along with emojis.
    Sends and receives messages via the chat room.
  #GUI:
  
    Built using the tkinter library.
    Displays received messages and provides an input box for new messages.
    Supports voting and vote-kicking.
#Requirements

    Python 3.x
    socket module (comes pre-installed with Python)
    threading module (comes pre-installed with Python)
    tkinter module (comes pre-installed with Python)
    emoji (optional for improved emoji support)
Install using:
```
pip install emoji

```
#Usage
  #Server
    To start the server open the command prompt and change the directory to the path of the file and type the following command:
```
python server.py

```
#Client
To start a client instance:

```

python client.py

```
#Explanation of Server Code

```
import socket
import threading

# Server information
HOST = '127.0.0.1'
PORT = 12345

# Creating a TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []
votes = {}

# Broadcast a message to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Handle vote-kicking
def handle_kick(nickname):
    index = nicknames.index(nickname)
    client = clients[index]
    clients.remove(client)
    nicknames.remove(nickname)
    broadcast(f'{nickname} has been kicked out!'.encode('utf-8'))
    client.close()

# Process individual client messages
def handle(client):
    while True:
        try:
            # Receive messages from the client
            message = client.recv(1024).decode('utf-8')
            if message.startswith('/kick'):
                # Handle voting logic for kicking a user
                _, target_nickname = message.split()
                if target_nickname in votes:
                    votes[target_nickname] += 1
                else:
                    votes[target_nickname] = 1

                if votes[target_nickname] > len(clients) // 2:
                    handle_kick(target_nickname)
                    del votes[target_nickname]
                else:
                    broadcast(f'Vote to kick {target_nickname}: {votes[target_nickname]}'.encode('utf-8'))
            else:
                broadcast(message.encode('utf-8'))
        except:
            # Remove client if the connection is lost
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} has left the chat!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Accept new client connections
def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        client.send('NICKNAME'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}')
        broadcast(f'{nickname} has joined the chat!'.encode('utf-8'))
        client.send('Connected to the server!'.encode('utf-8'))

        # Start handling thread for the client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print('Server is listening...')
receive()

```
````
```

  Server Setup:

    HOST and PORT define the server address.
    server is the socket object created with TCP and IPv4.
  Global Variables:

    clients stores connected client socket objects.
    nicknames stores client nicknames.
    votes manages votes for vote-kicking.
  Functions:

    broadcast(message) sends a message to all connected clients.
    handle_kick(nickname) removes a disruptive client after a successful vote.
    handle(client) manages messages for an individual client.
    receive() continuously listens for incoming client connections.
#Explanation of Client Code

  Client Setup:
    HOST and PORT specify the server address.
    Client class manages the GUI and server connection.
  Functions:

    __init__() initializes the client socket and starts the GUI and receive threads.
    gui_loop() sets up the graphical interface.
    write() sends messages to the server.
    vote_to_kick() sends a vote-kick request to the server.
    stop() stops the client and closes the connection.
    receive() listens for incoming messages from the server.
```
````
#Client Code
```

import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = '127.0.0.1'
PORT = 12345

class Client:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()
        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.pack(padx=20, pady=5)

        self.vote_kick_label = tkinter.Label(self.win, text="Kick Nickname:", bg="lightgray")
        self.vote_kick_label.pack(padx=20, pady=5)

        self.vote_input = tkinter.Entry(self.win)
        self.vote_input.pack(padx=20, pady=5)

        self.vote_button = tkinter.Button(self.win, text="Vote to Kick", command=self.vote_to_kick)
        self.vote_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def write(self):
        message = f'{self.nickname}: {self.input_area.get("1.0", "end")}'
        self.client.send(message.encode('utf-8'))
        self.input_area.delete("1.0", "end")

    def vote_to_kick(self):
        target_nickname = self.vote_input.get()
        vote_message = f'/kick {target_nickname}'
        self.client.send(vote_message.encode('utf-8'))
        self.vote_input.delete(0, tkinter.END)

    def stop(self):
        self.running = False
        self.win.destroy()
        self.client.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')

                if message == 'NICKNAME':
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message + '\n')
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("An error occurred!")
                self.client.close()
                break

client = Client(HOST, PORT)

```
#Explanation of Client Code

  #Client Setup:
  
    HOST and PORT specify the server address.
    Client class manages the GUI and server connection.
  Functions:
  
    __init__() initializes the client socket and starts the GUI and receive threads.
    gui_loop() sets up the graphical interface.
    write() sends messages to the server.
    vote_to_kick() sends a vote-kick request to the server.
    stop() stops the client and closes the connection.
    receive() listens for incoming messages from the server.
