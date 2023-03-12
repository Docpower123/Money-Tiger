import socket

# Create a UDP socket and bind it to a specific address and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 6000))

while True:
    # Receive a message from a client
    message, address = server_socket.recvfrom(1024)

    if message.decode() == "healthcheck":
        # Don't save health check response, just send it back to the load balancer
        response = "ok".encode()
    else:
        # Process the message (in this example, we just print it to the console)
        print(f"Received message: {message.decode()}")

        # Send a response to the client
        response = f"Received message: {message.decode()}".encode()

    server_socket.sendto(response, address)
