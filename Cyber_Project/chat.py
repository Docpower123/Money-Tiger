import tkinter as tk
from tkinter import font
import time
import threading
import queue
import random
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from settings import *
from socket import *


# security functions
def load_private_key(filename):
    with open(filename, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    return private_key


def load_public_key(filename):
    with open(filename, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key


def send_msg(client_socket, message, public_key, private_key, server_address):
    encrypted_message = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    signature = private_key.sign(
        encrypted_message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    client_socket.sendto(signature + encrypted_message, server_address)


def receive_response(client_socket, private_key, public_key):
    data, server_address = client_socket.recvfrom(RECV_SIZE)
    signature, encrypted_response = data[:256], data[256:]
    try:
        public_key.verify(
            signature,
            encrypted_response,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except:
        print("Invalid signature")
        client_socket.close()
        exit()
    decrypted_response = private_key.decrypt(
        encrypted_response,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_response, server_address


# parameters for the server to use
Server_ADDR = (S1_IP, S1_PORT)
ADDR = (CHAT_IP, random.randint(3000, 5999))
messages = queue.Queue()

# Load the private key from the PEM encoded file
private_key = load_private_key("private_key.pem")
# Load the public key from the PEM encoded file
public_key = load_public_key("public_key.pem")
# setting up the server
chat = socket(AF_INET, SOCK_DGRAM)
chat.bind(ADDR)
send_msg(chat, f'CHAT, {ADDR}'.encode(), public_key, private_key, Server_ADDR)


def get_info():
    while True:
        data, addr = receive_response(chat, private_key, public_key)
        if data.decode().split(',')[1] == 'MSG':
            messages.put((data, addr))


t = threading.Thread(target=get_info)


class ChatApp:
    def __init__(self, master, username):
        self.master = master
        self.master.title("Chat Room")
        self.master.geometry("500x700")
        self.master.configure(bg="#F5F5F5")

        # create chat history box
        self.history_box = tk.Text(self.master, state="disabled", width=50, height=30)
        self.history_box.configure(font=("Helvetica", 12))
        self.history_box.place(x=50, y=50)

        # create message box
        self.message_box = tk.Entry(self.master, width=33, font=("Helvetica", 12))
        self.message_box.place(x=50, y=600)
        self.message_box.bind("<Return>", self.send_message)

        # create send button
        self.send_button = tk.Button(self.master, text="Send", command=self.send_message, bg="#008CBA", fg="white",
                                     font=("Helvetica", 12))
        self.send_button.place(x=370, y=595, width=70, height=40)

        # username
        self.username = username

        # initialize message count and last message time
        self.message_count = 0
        self.last_message_time = 0
        self.is_blocked = False
        self.blocked_start_time = 0

        # set message limit and time limit in seconds
        self.message_limit = 5
        self.time_limit = 5
        self.block_time = 10

        # initialize list of bad words
        self.bad_words = ["bad", "word", "filter"]

    def send_message(self, event=None):
        # check if message count limit is reached
        current_time = time.time()
        if self.message_count >= self.message_limit and current_time - self.last_message_time < self.time_limit:
            time_left = int(self.time_limit - (current_time - self.last_message_time))
            self.history_box.configure(state="normal")
            self.history_box.insert("end",
                                    f"You are sending messages too quickly. Please wait {time_left} seconds before sending more messages.\n")
            self.history_box.configure(state="disabled")
            return

        # message
        message = self.message_box.get().strip()
        if not message: return

        # check if message contains bad words
        for bad_word in self.bad_words:
            if bad_word in message:
                self.history_box.configure(state="normal")
                self.history_box.insert("end", f"{username}: [Message Blocked]\n")
                self.history_box.configure(state="disabled")
                self.message_box.delete(0, "end")
                return

        # send message to server
        send_msg(chat, f'{self.username},MSG,{message}'.encode(), public_key, private_key, Server_ADDR)

        # add message to chat history and update message count and time
        self.history_box.configure(state="normal")
        self.history_box.insert("end", f"{self.username}: {message}\n")
        self.history_box.configure(state="disabled")
        self.message_box.delete(0, "end")
        self.message_count += 1
        self.last_message_time = current_time

        # auto scroll to bottom of chat history
        self.history_box.yview_moveto(1.0)

        # reset message count and allow sending messages again after 5 minutes
        if self.message_count >= self.message_limit and current_time - self.last_message_time >= self.time_limit * 5:
            self.message_count = 0

    def get_message(self):
        # updating messages from others
        if not messages.empty():
            other_msg, other_addr = messages.get()
            other_username = other_msg.decode().split(',')[0]
            other_msg = other_msg.decode().split(',')[2]
            if other_username != self.username:
                self.history_box.configure(state="normal")
                self.history_box.insert("end", f"{other_username}: {other_msg}\n")
                self.history_box.configure(state="disabled")
                self.message_count += 1

        root.after(100, self.get_message)


def run_chat(Username):
    global username
    username = Username
    t.start()

    global root
    root = tk.Tk()
    app = ChatApp(root, username)
    app.get_message()
    root.mainloop()
