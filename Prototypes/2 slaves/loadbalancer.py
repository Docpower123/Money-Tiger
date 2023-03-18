import socket
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt

# Server configuration
SERVER_HOST = "localhost"
SERVER_PORT = 6000

# Slave servers configuration
SLAVE_SERVERS = [('localhost', 7001), ('localhost', 7002)]


def find_most_populated_area(player_coords, margin=5):
    # Perform K-means clustering with k=2
    kmeans = KMeans(n_clusters=2).fit(player_coords)
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    # Find the largest cluster and return its center coordinates
    largest_cluster_label = max(set(labels), key=labels.tolist().count)
    largest_cluster_center = centroids[largest_cluster_label]

    # Find the coordinates of the bounding box of the largest cluster
    largest_cluster_points = np.array([p for i, p in enumerate(player_coords) if labels[i] == largest_cluster_label])
    x_min, y_min = np.min(largest_cluster_points, axis=0) - margin
    x_max, y_max = np.max(largest_cluster_points, axis=0) + margin

    # Find all players within the bounding box of the largest cluster
    players_in_area = [players_loc[0][i] for i, p in enumerate(players_loc[1]) if
                       x_min <= p[0] <= x_max and y_min <= p[1] <= y_max]

    return largest_cluster_center, x_min, y_min, x_max, y_max, players_in_area


# Create a UDP socket and bind it to a specific address and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 6000))

players_loc = [[], []]  # [player_ids], [player_coords]

while True:
    # Receive a message and the address of the sender
    message, addr = server_socket.recvfrom(1024)
    message = message.decode()
    if message.startswith('loc:'):
        print(message.split(':')[1].split(','))
        player_id, x, y = message.split(':')[1].split(',')
        x, y = float(x), float(y)
        # Update the location for a user
        if player_id in players_loc[0]:
            index = players_loc[0].index(player_id)
            players_loc[1][index] = (x, y)
        else:
            players_loc[0].append(player_id)
            players_loc[1].append((x, y))
        print(f"Received location from player {player_id}: ({x}, {y})")

        # Find the most populated area
        if len(players_loc[0]) > 1:
            center, x_min, y_min, x_max, y_max, players_in_area = find_most_populated_area(players_loc[1])
            message = f"area:{center[0]},{center[1]};{x_min},{y_min};{x_max},{y_max};{','.join(players_in_area)}".encode()
            print(f"Sending area to players: {message.decode()}")

            # Send the area message to one of the slave servers based on a simple round-robin algorithm
            next_slave_server = SLAVE_SERVERS[len(players_loc[0]) % len(SLAVE_SERVERS)]
            server_socket.sendto(message, next_slave_server)
