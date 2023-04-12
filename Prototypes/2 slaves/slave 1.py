import socket
import time

# Define the IP address and port number to listen on
HOST = 'localhost'  # Listen on all available network interfaces
PORT = 5000

# Create a UDP socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    # Bind the socket to the specified host and port
    s.bind((HOST, PORT))

    while True:
        # Receive a packet from the master server
        data, addr = s.recvfrom(1024)
        print(addr)
        # Simulate a delay in processing the request to simulate server load
        #time.sleep(0.5)

        # Send a response packet back to the master server
        if data == b'Health check':
            s.sendto(b'OK', addr)





