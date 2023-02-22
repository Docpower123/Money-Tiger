from socket import *
from time import ctime
import threading
import queue
import random

clients = []

# parameters for the server to use
HOST = '192.168.1.168'
PORT = 9998
ADDR = (HOST, PORT)

# setting up the server
slave1 = socket(AF_INET, SOCK_DGRAM)
slave1.bind(ADDR)
print('slave 1 is up and running!')
slave1.sendto(f"Check_Num:{random.randint(1, 100000)}".encode(), ("192.168.1.168", 9999))


def recive_from_master():
    while True:
        message, addr1 = slave1.recvfrom(1024)
        if addr1[1] == 9999:
            print(message.decode())


recive_from_master()
