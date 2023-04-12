import socket
import time
import threading
import random


def update_server_status(slave_servers, timeout=5, max_rtt=100):
    """
    Perform a health check on a dictionary of slave servers using UDP sockets and update the original dictionary with the server status.

    Args:
        slave_servers (dict): A dictionary of slave servers with keys as server names and values as (ip_address, port) tuples.
        timeout (float): The timeout value for the health check in seconds. Default is 5 seconds.
        max_rtt (float): The maximum round-trip time allowed in milliseconds. If the round-trip time is longer than this, the server is considered overloaded. Default is 100 milliseconds.
    """
    # Create a UDP socket for sending health check packets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    # Loop through the slave servers and perform a health check on each one
    for server_address, status in slave_servers.items():
        # Send a health check packet to the server
        start_time = time.time()
        message = b"Health check"
        sock.sendto(message, server_address)

        # Wait for a response from the server
        try:
            data, address = sock.recvfrom(1024)
            end_time = time.time()

            # Check that the response is valid
            if data == b'OK':
                # Calculate the round-trip time and update the status
                rtt = (end_time - start_time) * 1000  # Convert to milliseconds
                is_healthy = True
                is_overloaded = rtt > max_rtt
            else:
                is_healthy = False
                is_overloaded = False
                rtt = None
        except:
            # If no response is received, mark the server as unhealthy and not overloaded
            is_healthy = False
            is_overloaded = False
            rtt = None
        try:
            # Update the dictionary with the server status
            slave_servers[server_address] = (is_healthy, is_overloaded, rtt)
        except:
            print('server down')

    # Close the socket
    sock.close()


def move_players_to_new_server(player_locations, current_server, slave_servers):
    # Create a UDP socket for sending health check packets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Find a new server that is online
    online_servers = [server_name for server_name, server_status in slave_servers.items() if server_status[0]]
    new_server = random.choice(online_servers)

    # Move players from the current server to the new server
    for player_id, player_location in player_locations.items():
        if player_location == current_server:
            player_locations[player_id] = new_server
            print(f'Moving {player_id} from {current_server} to {new_server}')

    # Wait for the new server to update its player location information
    time.sleep(0.5)

    # Notify the new server that it has new players
    message = 'new_players'
    new_server_address = new_server
    sock.sendto(message.encode(), new_server_address)
    print('players moved')
    # Close the socket
    sock.close()


def Check_servers():
    while True:
        # Perform a health check on the slave servers
        update_server_status(slave_servers)
        try:
            # Print the updated status of the slave servers
            for server_name, server_status in slave_servers.items():
                is_healthy, is_overloaded, rtt = server_status
                if is_healthy:
                    if is_overloaded:
                        print(f"{server_name} is healthy but overloaded (RTT: {rtt} ms)")
                        move_players_to_new_server(players, server_name, slave_servers)
                    else:
                        print(f"{server_name} is healthy (RTT: {rtt} ms)")
                else:
                    print(f"{server_name} is dead")
                    move_players_to_new_server(players, server_name, slave_servers)

        except:
            pass
        # Wait for 10 seconds
        time.sleep(10)


def assign_areas(slave_servers):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Define the game map size and the number of server areas
        map_width = 650
        map_height = 450
        servers = [server_name for server_name, server_status in slave_servers.items() if server_status[0]]
        num_server_areas = len(servers)
        if num_server_areas == 0:
            print('No servers are online!')
            return
        # Divide the game map into rectangular areas
        server_areas = []
        area_width = map_width // num_server_areas
        for i in range(num_server_areas):
            area_left = i * area_width
            area_right = (i + 1) * area_width
            area_height = map_height
            area = (area_left, 0, area_right, area_height)
            if area not in assigned_areas.values():
                server_name = servers[i]
                sock.sendto(f'new area assigned: {area}'.encode(), server_name)
                assigned_areas[server_name] = area
                print(f"Assigned {area} to {server_name}")
        time.sleep(5)


def get_player_area(server_areas, sock):
    """
    Determines which server area the player belongs to based on their coordinates.
    """
    data, addr = sock.recvfrom(1024)
    if data.decode().startswith('coords:'):
        player_coords = data.decode().split(':')[1]
        player_coords = tuple(map(int, player_coords.split(',')))  # Convert to integers
        for i, area, in enumerate(server_areas.values()):
            if int(player_coords[0]) >= area[0] and int(player_coords[0]) <= area[2] and int(player_coords[1]) >= area[1] and \
                    int(player_coords[1]) <= area[3]:
                sock.sendto(f'new area assigned: {area}'.encode(), addr)
                return
        # If the player is not within any server area, return -1
        print(-1)




# Define the slave servers as a dictionary with server names as keys and (ip_address, port) tuples as values
slave_servers = {
    ("localhost", 5000): ("localhost", 5000),
    ("localhost", 5001): ("localhost", 5001)
}

players = {
    ('localhost', 6000): ('localhost', 5000)
}

assigned_areas = {}

# Define the IP address and port number to listen on
HOST = 'localhost'  # Listen on all available network interfaces
PORT = 9000

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

Health_monitoring = threading.Thread(target=Check_servers)
Health_monitoring.start()
time.sleep(3.5)
area_assiging = threading.Thread(target=assign_areas, args=(slave_servers,))
area_assiging.start()

assign_players = threading.Thread(target=get_player_area, args=(assigned_areas, sock,))
assign_players.start()


