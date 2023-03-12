import socket
import json
import time

# Define the list of servers and their current loads
servers = {
    'server1': {
        'address': ('localhost', 6000),
        'load': 0,
        'health': True
    },
    'server2': {
        'address': ('localhost', 6002),
        'load': 0,
        'health': True
    },
    'server3': {
        'address': ('localhost', 6003),
        'load': 0,
        'health': True
    }
}

# Define the health check interval and timeout
HEALTH_CHECK_INTERVAL = 5  # seconds
HEALTH_CHECK_TIMEOUT = 2   # seconds

# Create a UDP socket and bind it to a specific port
load_balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
load_balancer_socket.bind(('localhost', 9000))

# Perform initial health checks on servers
for server_name, server_info in servers.items():
    server_address = server_info['address']
    try:
        load_balancer_socket.sendto(b'health_check', server_address)
        response, _ = load_balancer_socket.recvfrom(1024)
        if response.decode() == 'ok':
            print(f"Server {server_name} at address {server_address} is up")
        else:
            print(f"Server {server_name} at address {server_address} is down")
            server_info['health'] = False
    except Exception as e:
        print(f"Server {server_name} at address {server_address} is down: {e}")
        server_info['health'] = False

while True:
    # Perform health checks on servers at regular intervals
    time.sleep(HEALTH_CHECK_INTERVAL)
    for server_name, server_info in servers.items():
        if not server_info['health']:
            continue
        server_address = server_info['address']
        try:
            load_balancer_socket.sendto(b'health_check', server_address)
            response, _ = load_balancer_socket.recvfrom(1024)
            if response.decode() != 'ok':
                print(f"Server {server_name} at address {server_address} is down")
                server_info['health'] = False
        except Exception as e:
            print(f"Server {server_name} at address {server_address} is down: {e}")
            server_info['health'] = False

    # Receive a message from a client
    message, address = load_balancer_socket.recvfrom(1024)

    # Find the least loaded and healthy server
    least_loaded_server = None
    for server_name, server_info in servers.items():
        if server_info['health']:
            if least_loaded_server is None or server_info['load'] < servers[least_loaded_server]['load']:
                least_loaded_server = server_name

    if least_loaded_server is None:
        print("No healthy servers available")
        continue

    # Forward the message to the least loaded and healthy server
    server_address = servers[least_loaded_server]['address']
    load_balancer_socket.sendto(message, server_address)

    # Increment the load of the least loaded server
    servers[least_loaded_server]['load'] += 1

load_balancer_socket.close()
