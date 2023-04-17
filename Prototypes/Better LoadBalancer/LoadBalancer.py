import json
import logging
import socket
import threading
import time
from queue import Queue

# Global configuration parameters
SERVER_HOST = "localhost"
SERVER_PORT = 5000
LOAD_THRESHOLD = 0.7
MOVE_THRESHOLD = 0.9
PERFORMANCE_CHECK_INTERVAL = 30
PROXIMITY_THRESHOLD = 10

# Data structures to store server and player information
server_info = {}
player_info = {}
server_load = {}
packet_queue = Queue()


# Function to start a server
def start_server(address):
    # Create a UDP socket for the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(address)
    return sock


# Function to stop a server
def stop_server(sock):
    sock.close()


# Function to register a server with the load balancer
def register_server(address, capacity):
    # Create a socket for the server
    sock = start_server(address)

    # Add the server to the server_info dictionary
    server_info[address] = {"socket": sock, "capacity": capacity, "players": set()}

    # Log the registration
    logging.info(f"Server registered at {address} with capacity {capacity}.")


# Function to unregister a server with the load balancer
def unregister_server(address):
    # Stop the server
    stop_server(server_info[address]["socket"])

    # Remove the server from the server_info dictionary
    del server_info[address]

    # Log the unregistration
    logging.info(f"Server unregistered at {address}.")


# Function to add a player to a server
def add_player(server_address, player_id, position):
    # Add the player to the player_info dictionary
    player_info[player_id] = {"server": server_address, "position": position}

    # Add the player to the set of players on the server
    server_info[server_address]["players"].add(player_id)

    # Log the player addition
    logging.info(f"Player {player_id} added to server at {server_address} at position {position}.")


# Function to remove a player from a server
def remove_player(server_address, player_id):
    # Remove the player from the player_info dictionary
    del player_info[player_id]

    # Remove the player from the set of players on the server
    server_info[server_address]["players"].remove(player_id)

    # Log the player removal
    logging.info(f"Player {player_id} removed from server at {server_address}.")
