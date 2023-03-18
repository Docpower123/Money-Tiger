import socket
import time

# Server configuration
SERVER_HOST = "localhost"
SERVER_PORT = 6000

# Client configuration
CLIENT_ID = "1"
LOCATION_UPDATE_INTERVAL = 5

# Create a UDP socket and bind it to a specific address and port
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('localhost', 7000 + int(CLIENT_ID)))

while True:
    # Get the current location of the player
    x, y = input("Enter your location (comma-separated): ").split(",")
    message = f"loc:{CLIENT_ID},{x},{y}".encode()
    # Send the location to the server
    client_socket.sendto(message, (SERVER_HOST, SERVER_PORT))
    # Wait for the server to send back the most populated area
    message, addr = client_socket.recvfrom(1024)
    message = message.decode()
    if message.startswith('area:'):
        area_data = message.split(':')[1].split(';')
        area_center = tuple(map(float, area_data[0].split(',')))
        area_bounds = tuple(map(float, area_data[1].split(',')))
        players_in_area = area_data[2].split(',')
        print(f"Received area from server: center={area_center}, bounds={area_bounds}, players={players_in_area}")
    # Wait for the next location update interval
    time.sleep(LOCATION_UPDATE_INTERVAL)
