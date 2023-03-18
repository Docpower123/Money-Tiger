import socket

# Slave configuration
SLAVE_HOST = "localhost"
SLAVE_PORT = 7002

# Create a UDP socket and bind it to a specific address and port
slave_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
slave_socket.bind((SLAVE_HOST, SLAVE_PORT))

while True:
    # Receive a message and the address of the sender
    message, addr = slave_socket.recvfrom(1024)
    message = message.decode()
    if message.startswith('area:'):
        area_info = message.split(':')[1].split(';')
        center = tuple(map(float, area_info[0].split(',')))
        bounding_box = tuple(map(float, area_info[1].split(',')))
        players_in_area = area_info[2].split(',')
        print(
            f"Received area info from load balancer: center={center}, bounding_box={bounding_box}, players={players_in_area}")

        # Serve players in this area
        while True:
            # Receive a message from a player
            player_message, player_addr = slave_socket.recvfrom(1024)
            player_message = player_message.decode()
            player_id, x, y = player_message.split(',')
            x, y = float(x), float(y)
            print(f"Received location from player {player_id}: ({x}, {y})")

            # Check if the player is in this area
            if bounding_box[0] <= x <= bounding_box[2] and bounding_box[1] <= y <= bounding_box[3]:
                print(f"Player {player_id} is in this area")
                response_message = f"You are in area {center}, there are {len(players_in_area)} players in this area".encode()
                slave_socket.sendto(response_message, player_addr)
            else:
                print(f"Player {player_id} is not in this area")
