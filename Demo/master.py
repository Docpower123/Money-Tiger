from socket import *
from time import ctime
import threading
import queue

clients = []
slaves = []

# parameters for the server to use
HOST = '192.168.1.168'
PORT = 9999
ADDR = (HOST, PORT)

# setting up the server
master = socket(AF_INET, SOCK_DGRAM)
master.bind(ADDR)
print('master is up and running!')



def recive():
    while True:
        _, addr = master.recvfrom(1024)
        if str(addr[1]).startswith('9'):
            slaves.append(addr)
        if addr not in clients and addr not in slaves:
            clients.append(addr)
            """
            code to check for the best server to connect to
            """
            server = slaves[0]
            master.sendto(f'{server}'.encode(), addr)
            master.sendto(f'{addr}'.encode(), server)



recive()