import socket
import time
import threading
import random
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import mysql.connector

def load_private_key(filename):
    with open(filename, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    return private_key


def load_public_key(filename):
    with open(filename, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key


def receive_message(server_socket, private_key, public_key):
    data, client_address = server_socket.recvfrom(1024)
    signature, encrypted_message = data[:256], data[256:]
    try:
        public_key.verify(
            signature,
            encrypted_message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except:
        print("Invalid signature")
        server_socket.close()
        return
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message, client_address


def send_response(server_socket, response, public_key, private_key, client_address):
    encrypted_response = public_key.encrypt(
        response,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    signature = private_key.sign(
        encrypted_response,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    server_socket.sendto(signature + encrypted_response, client_address)


def update_server_status(slave_servers, private_key, public_key, timeout=5, max_rtt=300):
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
        message = b"Health check"
        send_response(sock, message, public_key, private_key, server_address)
        start_time = time.time()
        # Wait for a response from the server
        try:
            data, addr = receive_message(sock, private_key, public_key)
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


def move_players_to_new_server(player_locations, current_server, slave_servers, private_key, public_key):
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
    send_response(sock, message.encode(), public_key, private_key, new_server_address)
    # Close the socket
    sock.close()


def Check_servers(slave_servers, private_key, public_key):
    while True:
        # Perform a health check on the slave servers
        update_server_status(slave_servers, private_key, public_key)
        try:
            # Print the updated status of the slave servers
            for server_name, server_status in slave_servers.items():
                is_healthy, is_overloaded, rtt = server_status
                if is_healthy:
                    if is_overloaded:
                        print(f"{server_name} is healthy but overloaded (RTT: {rtt} ms)")
                        move_players_to_new_server(players, server_name, slave_servers, private_key, public_key)
                    else:
                        print(f"{server_name} is healthy (RTT: {rtt} ms)")
                else:
                    print(f"{server_name} is dead")
                    move_players_to_new_server(players, server_name, slave_servers, private_key, public_key)

        except:
            pass
        # Wait for 10 seconds
        time.sleep(10)


def assign_areas(slave_servers, private_key, public_key):
    global assigned_areas
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Define the game map size and the number of server areas
        map_width = 650
        map_height = 450
        servers = [server_name for server_name, server_status in slave_servers.items() if server_status[0]]
        num_server_areas = len(servers)
        if num_server_areas == 0:
            print('No servers are up!')
        else:
            # Divide the game map into rectangular areas
            server_areas = []
            overlap = 50  # adjust as needed
            area_width = (map_width + overlap) // num_server_areas
            for i in range(num_server_areas):
                area_left = i * area_width - overlap
                area_right = (i + 1) * area_width + overlap
                area_height = map_height
                area = (area_left, 0, area_right, area_height)
                if area not in assigned_areas.values():
                    server_name = servers[i]
                    send_response(sock, f'new area assigned: {area}'.encode(), public_key, private_key, server_name)
                    assigned_areas[server_name] = area
                    print(f"Assigned {area} to {server_name}")
        time.sleep(3)


def get_player_area(server_areas, sock, players, data, addr, private_key, public_key):
    """
    Determines which server area the player belongs to based on their coordinates.
    """
    time = 0
    if data.startswith(b'coords:'):
        player_coords = data.split(b':')[1]
        player_coords = tuple(map(int, player_coords.split(b',')))  # Convert to integers
        for server_ip, area in server_areas.items():
            if int(player_coords[0]) >= area[0] and int(player_coords[0]) <= area[2] and int(player_coords[1]) >= \
                    area[
                        1] and \
                    int(player_coords[1]) <= area[3]:
                time += 1
                if time >= 2:
                    first = players[addr]
                    second = server_ip
                    players[addr] = f'{first};{second}'
                    return
                send_response(sock, f'new area assigned: {area}:{addr}'.encode(), public_key, private_key, addr)
                print(f'new area assigned: {area}:{addr}'.encode(), addr)
                if addr[0] in players:
                    players[addr] = server_ip
                else:
                    players.update({addr: server_ip})


def forward_data(socket, players, assigned_areas, client_data):
    while True:
        items_to_remove = []
        for addr, data in client_data.items():
            message = data
            if message.decode().find(';') != -1 and message.decode().split(';')[1] == "DBS":
                messag = message.decode().split(';')
                info_name = messag[2]
                for i in range(3):
                    messag.pop(0)
                t = tuple(messag)
                sql = f"update dblogin set {info_name} = %s where Username = %s"
                mycur.execute(sql, t)
                db.commit()

            # get info from database
            elif message.decode().find(',') != -1 and message.decode().split(',')[1] == "DBG":
                messag = message.decode().split(',')
                info_name = messag[2]
                user_password = messag[3]
                user_name = messag[0]
                # get info from database
                sql = f"select {info_name} from dblogin where Username = %s and Password = %s"
                mycur.execute(sql, [(user_name), (user_password)])
                info = mycur.fetchall()
                # send info to client
                send_response(loadbalancer, f"SERVER,DBG,{info[0][0]}".encode(), public_key, private_key, addr)

            # log varify
            elif message.decode().find(',') != -1 and message.decode().split(',')[1] == "LV":
                user_varify = message.decode().split(',')[2]
                pass_varify = message.decode().split(',')[3]
                sql = "select * from dblogin where Username = %s and Password = %s"
                mycur.execute(sql, [(user_varify), (pass_varify)])
                results = mycur.fetchall()
                if results:
                    send_response(loadbalancer, "SERVER,LV,T".encode(), public_key, private_key, addr)
                else:
                    send_response(loadbalancer, "SERVER,LV,F".encode(), public_key, private_key, addr)

            # register new clients
            elif message.decode().find(',') != -1 and message.decode().split(',')[1] == "REG":
                username = message.decode().split(',')[2]
                password = message.decode().split(',')[3]
                sql = "insert into dblogin (Username, Password) values(%s,%s)"
                t = (username, password)
                mycur.execute(sql, t)
                db.commit()

            if data.decode()[0:4] == "KILL":
                clients.remove(addr)

            if data.startswith(b'coords:'):
                print('hello! this is the begining!')
                print(client_data)
                get_player_area(assigned_areas, socket, players, data, addr, private_key, public_key)
                items_to_remove.append(addr)
                print('hello! this is the end!')
                print(client_data)
            else:
                if addr not in client_data:
                    client_data[addr] = []
                    client_data[addr].append(data)
                else:
                    for ad, server_addr in players.items():
                        if addr == ad:
                            try:
                                if players.get(ad, '').split(';'):
                                    # Retrieve the value associated with the addr key from the players dictionary
                                    addr_value = players.get(ad, '')

                                    # Split the string into individual server addresses using the semicolon separator
                                    server_addresses = addr_value.split(';')

                                    # Send the data to each server address
                                    for server_address in server_addresses:
                                        for client_data_item in client_data[addr]:
                                            send_response(socket, data, public_key, private_key, eval(server_address))
                            except:
                                send_response(socket, data, public_key, private_key, server_addr)
                    if addr == server_addr:
                        send_response(socket, data, public_key, private_key, addr)
        for addr in items_to_remove:
            del client_data[addr]


def receive(client_data, loadbalancer, private_key, public_key):
    while True:
        data, addr = receive_message(loadbalancer, private_key, public_key)
        client_data[addr] = (data)
        print(client_data)


# Define the slave servers as a dictionary with server names as keys and (ip_address, port) tuples as values
slave_servers = {
    ("localhost", 5000): ("localhost", 5000),
    ("localhost", 5001): ("localhost", 5001)
}

client_data = {}
players = {}
assigned_areas = {}

# Define the IP address and port number to listen on
HOST = 'localhost'  # Listen on all available network interfaces
PORT = 9000

# Load the private key from the PEM encoded file
private_key = load_private_key("private_key.pem")
# Load the public key from the PEM encoded file
public_key = load_public_key("public_key.pem")
# connecting to the database
db = mysql.connector.connect(host="mysql-serve", port="3306", user="client", passwd="P123321p", database="dblogin",
                             auth_plugin='mysql_native_password')
mycur = db.cursor()
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

Health_monitoring = threading.Thread(target=Check_servers, args=(slave_servers, private_key, public_key))
Health_monitoring.start()
time.sleep(3.5)
area_assiging = threading.Thread(target=assign_areas, args=(slave_servers, private_key, public_key))
area_assiging.start()
# assign_players = threading.Thread(target=get_player_area, args=(assigned_areas, sock, players,))
# assign_players.start()
forward_data = threading.Thread(target=forward_data, args=(sock, players, assigned_areas, client_data))
forward_data.start()

# receive all transmission and decrypt it
receive = threading.Thread(target=receive, args=(client_data, sock, private_key, public_key))
receive.start()

# fix line 88
# fix exit in receive func

