from socket import *

# parameters for the server to use
HOST = '192.168.1.161'
PORT = 9996
ADDR = (HOST, PORT)
Client_addr = ()
# setting up the server
slave = socket(AF_INET, SOCK_DGRAM)
slave.bind(ADDR)
slave.sendto(f'{ADDR}'.encode(), ('192.168.1.161', 9999))
while True:
    data, addr = slave.recvfrom(1024)
    if data.decode() == 'done':
        break

print('slave is up and running!')

while True:
    data, addr = slave.recvfrom(1024)
    if data.decode():
        Client_addr = eval(data.decode())
        break

while True:
    data, addr = slave.recvfrom(1024)
    if data.decode() and addr == Client_addr:
        cords = data.decode().split(',')
        print(cords[0], cords[1])
        cords[0] = cords[1]
        slave.sendto(f'{cords[0]}, {cords[1]}'.encode(), Client_addr)