import socket

# Create a UDP socket and bind it to a specific address and port
slave_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
slave_socket.bind(('192.168.1.113', 9999))

while True:
    # Receive a message and the address of the sender
    message, addr = slave_socket.recvfrom(1024)
    message = message.decode()
    print(message)
