# Client.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox


class ChatClient:
    def __init__(self, nickname, server_ip, port=5555):
        self.nickname = nickname
        self.server_ip = server_ip
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

        # GUI setup
        self.window = tk.Tk()
        self.window.title(f"LAN Chat - {self.nickname}")
        self.window.geometry("600x300")
        self.window.minsize(400, 200)

        # Chat area (scrolled text)
        self.chat_area = scrolledtext.ScrolledText(self.window)
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.chat_area.config(state=tk.DISABLED)

        # Frame for entry and button
        self.input_frame = tk.Frame(self.window)
        self.input_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Message entry (Unicode supported)
        self.message_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.message_entry.bind("<Return>", self.send_message)

        # Kick button
        self.kick_button = tk.Button(self.input_frame, text="Kick", command=self.kick_user)
        self.kick_button.pack(side=tk.RIGHT, padx=5)

        # Resize behavior
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Connection and message threads
        self.connect_to_server()
        self.thread_receive = threading.Thread(target=self.receive)
        self.thread_receive.daemon = True
        self.thread_receive.start()

    def send_initial_data(self):
        self.client.send(self.nickname.encode('UTF-16'))
        self.log("Connected to server!")

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('UTF-16')
                if message:
                    self.log(message)
                if message == 'You have been kicked out!':
                    self.log("You have been kicked from the chat.")
                    self.client.close()
                    break
            except socket.error as e:
                self.log(f"Disconnected from server: {e}")
                self.client.close()
                messagebox.showerror("Connection Error", "You have been disconnected from the server.")
                break

    def send_message(self, event=None):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        if message.startswith('/kick'):
            command = f'/kick {message.split()[1]}'
            try:
                self.client.send(command.encode('UTF-16'))
            except socket.error as e:
                self.log(f"Failed to send command: {e}")
                messagebox.showerror("Connection Error", "Unable to send the command to the server.")
        else:
            full_message = f'{self.nickname}: {message}'
            try:
                self.client.send(full_message.encode('UTF-16'))
            except socket.error as e:
                self.log(f"Failed to send message: {e}")
                messagebox.showerror("Connection Error", "Unable to send the message to the server.")

    def kick_user(self):
        target_nickname = self.message_entry.get()
        if not target_nickname:
            messagebox.showwarning("Kick Warning", "Please specify a nickname to kick.")
            return

        command = f'/kick {target_nickname}'
        try:
            self.client.send(command.encode('UTF-16'))
            self.log(f'Attempting to kick {target_nickname}')
        except socket.error as e:
            self.log(f"Failed to send command: {e}")
            messagebox.showerror("Connection Error", "Unable to send the command to the server.")

    def connect_to_server(self):
        try:
            self.client.connect((self.server_ip, self.port))
            self.send_initial_data()
            self.connected = True
        except socket.error as e:
            self.log(f"Unable to connect to server: {e}")
            messagebox.showerror("Connection Error", "Failed to connect to the server.")
            self.window.destroy()

    def log(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.yview(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    nickname = input("Choose your nickname: ")
    server_ip = input("Enter server IP address: ")
    chat_client = ChatClient(nickname, server_ip)
    chat_client.run()
