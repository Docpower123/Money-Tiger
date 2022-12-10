from socket import *
from time import ctime
import threading
import queue

messages = queue.Queue()
clients = []

HOST = '192.168.1.104'
PORT = 9999
BUFSIZE = 1024
ADDR = (HOST, PORT)

master = socket(AF_INET, SOCK_DGRAM)
master.bind(ADDR)
print('Server is up and running!')


def receive():
    while True:
        message, addr = master.recvfrom(1024)
        messages.put((message, addr))


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            print(message.decode())
            if addr not in clients:
                clients.append(addr)
            for client in clients:
                try:
                    if message.decode().startswith("SIGNUP_TAG:"):
                        name = message.decode()[message.decode().index(':') + 1:]
                        print('got here! ')
                        master.sendto(f"{name} Joined!", client)
                    else:
                        master.sendto(message)
                except:
                    clients.remove(client)


t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()

# while True:
#    print("...waiting for message...")
#    data, ADDR = master.recvfrom(BUFSIZE)
#    data = data.decode()
#    if data is None:
#        break
#    print("[%s]: From Address %s:%s receive data: %s" % (ctime(), ADDR[0], ADDR[1], data))

#   send_data = ("> ").encode()
#   if send_data is not None:
#      master.sendto(send_data, ADDR)
# master.close()
