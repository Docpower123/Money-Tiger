from socket import *
from time import ctime
import threading
import queue

messages = queue.Queue()
clients = []

# parameters for the server to use
HOST = '192.168.174.95'
PORT = 9999
ADDR = (HOST, PORT)

# setting up the server
master = socket(AF_INET, SOCK_DGRAM)
master.bind(ADDR)
print('Server is up and running!')

"""
a simple function that receive the message from the client and put the message and addr in the array  
"""


def receive():
    while True:
        message, addr = master.recvfrom(1024)
        messages.put((message, addr))


"""
a function that goes through the messages and broadcast them to all the clients
"""


def broadcast():
    blacklist = 'hi'
    while True:
        while not messages.empty():
            message, addr = messages.get()
            if addr not in clients:
                clients.append(addr)
            for client in clients:
                try:
                    if client != blacklist:
                        if message.decode().startswith('SIGNUP_TAG:'):
                            name = message.decode()[message.decode().index(':') + 1:]
                            master.sendto(f'{name} joined! from: {addr[0]} at: {ctime()[11:16]}'.encode(), client)
                        elif message.decode().find('sudo'):
                             blacklist = addr
                        else:
                            master.sendto(message, client)
                except:
                    clients.remove(client)


# create and start the processes

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
