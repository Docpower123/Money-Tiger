from socket import *
import queue
import threading

# parameters for the server to use
HOST = '192.168.173.149'
PORT = 9996
ADDR = (HOST, PORT)
clients = []
messages = queue.Queue()

# setting up the server
slave = socket(AF_INET, SOCK_DGRAM)
slave.bind(ADDR)
slave.sendto(f'{ADDR}'.encode(), ('192.168.173.149', 9999))


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


while True:
    data, addr = slave.recvfrom(1024)
    if data.decode() == 'done':
        break

print('slave is up and running!')

while True:
    data, addr = slave.recvfrom(1024)
    if data.decode():
        clients.append(eval(data.decode()))
        break

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
