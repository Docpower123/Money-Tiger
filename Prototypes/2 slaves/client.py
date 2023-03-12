import socket

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # Send a message to the load balancer
    message = "Hello, world!".encode()
    client_socket.sendto(message, ('localhost', 9000))

    # Receive a response from the server
    response, server_address = client_socket.recvfrom(1024)
    print(f"Received response from {server_address}: {response.decode()}")

    # Wait for a bit before sending another message
    input("Press Enter to send another message...")
