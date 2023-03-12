from socket import *

# Parameters for the server to use
HOST = 'localhost'
PORT = 5003
ADDR = (HOST, PORT)

# Setting up the server
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(ADDR)
print(f'server 3: Server is up and running at {ADDR}')

# Handling incoming requests
while True:
    data, addr = server_socket.recvfrom(1024)
    print(f'Request received from {addr}: {data.decode()}')
    server_socket.sendto(b'PONG', addr)
