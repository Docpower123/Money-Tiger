from socket import *

# parameters for the server to use
HOST = '192.168.175.248'
PORT = 9996
ADDR = (HOST, PORT)

# setting up the server
slave = socket(AF_INET, SOCK_DGRAM)
slave.bind(ADDR)
slave.sendto(f'{ADDR}'.encode(), ('192.168.175.248', 9999))
while True:
    data, addr = slave.recvfrom(1024)
    if data.decode() == 'done':
        break

print('slave is up and running!')
