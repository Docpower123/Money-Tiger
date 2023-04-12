import socket
import time

# Create a UDP socket and bind it to a specific address and port
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
player_coords = '200, 100'
client.sendto(f'coords:{player_coords}'.encode(), ('localhost', 9000))
while True:
    # Receive a message and the address of the sender
    message, addr = client.recvfrom(1024)
    message = message.decode()
    print(message)
    time.sleep(1.5)
    client.sendto('hello!'.encode(), ('localhost', 9000))