from socket import *
from settings import *
import queue
import threading

# parameters for the server to use
HOST = S1_IP
PORT = S1_PORT
ADDR = (HOST, PORT)
clients = []
messages = queue.Queue()

# setting up the server
slave = socket(AF_INET, SOCK_DGRAM)
slave.bind(ADDR)
slave.sendto(f'{ADDR}'.encode(), (LB_IP, LB_PORT))


def receive():
    while True:
        message, addr = slave.recvfrom(1024)
        messages.put((message, addr))


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            for client in clients:
                slave.sendto(f'{message.decode()}'.encode(), client)


def find_clients():
    while True:
        data, addr = slave.recvfrom(1024)
        if data.decode():
            the_data = data.decode()
            if the_data[0:2] == 'IP':
                clients.append(eval(the_data[2:]))
                if len(clients) == 2:
                    break


while True:
    data, addr = slave.recvfrom(1024)
    if data.decode() == 'done':
        break

print('slave is up and running!')

find_clients()

#t1 = threading.Thread(target=find_clients)
t2 = threading.Thread(target=receive)
t3 = threading.Thread(target=broadcast)

#t1.start()
t2.start()
t3.start()

