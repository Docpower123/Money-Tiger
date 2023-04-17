import socket
import time
import threading

# Create a UDP socket and bind it to a specific address and port
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
player_coords = '50, 100'
client.sendto(f'coords:{player_coords}'.encode(), ('localhost', 9000))
client.settimeout(2.0)  # set timeout to 1 second
while True:
    client.sendto('hello! 2'.encode(), ('localhost', 9000))
    try:
        # Receive a message and the address of the sender
        message, addr = client.recvfrom(1024)
        message = message.decode()
        print(message)
        client.sendto('hoi!'.encode(), ('localhost', 9000))
        print('sent!')
    except socket.timeout:
        print('Timed out waiting for server response')
