from socket import *
from settings import *
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from random import choice
from arcade import load_tilemap, Sprite, PhysicsEngineSimple
import queue
import threading
import math
import time
import random
import pathlib
import numpy as np

# parameters for the server to use
HOST = gethostbyname(gethostname())
PORT = S1_PORT
ADDR = (HOST, PORT)
JOIN_COOLDOWN = 30
clients = []
chats = []
messages = queue.Queue()


# security functions
def load_private_key(filename):
    with open(filename, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    return private_key


def load_public_key(filename: str):
    with open(filename, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key


def receive_message(server_socket: socket, private_key, public_key):
    try:
        data, client_address = server_socket.recvfrom(RECV_SIZE)
        signature, encrypted_message = data[:256], data[256:]
        public_key.verify(
            signature,
            encrypted_message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        decrypted_message = private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_message, client_address
    except Exception as e:
        print(f"Error while receiving message: {e}")


def send_response(server_socket, response, public_key, private_key, client_address):
    try:
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
    except Exception as e:
        print(f"Error while sending response: {e}")


# Load the private key from the PEM encoded file
private_key = load_private_key("private_key.pem")
# Load the public key from the PEM encoded file
public_key = load_public_key("public_key.pem")
# setting up the server
with socket(AF_INET, SOCK_DGRAM) as slave:
    slave.bind(ADDR)
    send_response(slave, f"{ADDR}".encode(), public_key, private_key, (gethostbyname(gethostname()), LB_PORT))

# Game
layer_options = {LAYER_NAME_BARRIER: {"use_spatial_hash": True}}

TILED_MAP = pathlib.Path("./map/map.json")
tile_map = load_tilemap(TILED_MAP, TILE_SIZE, layer_options=layer_options)
players_dict = {}
enemies_sprites_list = []
enemies_physics = []
enemies_names = []
enemies_health = []
enemies_died = []
enemies_died_time = []


# ------------------ enemies ------------------

def get_player_distance_direction(players_dict, e_pos):
    # get distance and direction from enemies to nearest player
    p_cords = np.array(list(players_dict.values()), dtype=float)
    e_pos = np.array(e_pos, dtype=float)
    distance_vec = p_cords - e_pos
    distance = np.linalg.norm(distance_vec, axis=1)
    min_distance_idx = np.argmin(distance)
    min_distance_vec = distance_vec[min_distance_idx]
    min_distance = distance[min_distance_idx]

    if min_distance > 0:
        if min_distance_vec[0] < 0 and min_distance_vec[1] < 0:
            direction = (-1, -1)
        elif min_distance_vec[0] > 0 and min_distance_vec[1] > 0:
            direction = (1, 1)
        elif min_distance_vec[0] < 0 < min_distance_vec[1]:
            direction = (-1, 1)
        else:
            direction = (1, -1)
    else:
        direction = (0, 0)

    return min_distance, direction


def get_status(enemy_data, e_pos, name):
    # get status for the enemy based on distance to nearest player
    distance = get_player_distance_direction(players_dict, e_pos)[0]
    notice_radius = enemy_data[name]['notice_radius']
    attack_radius = enemy_data[name]['attack_radius']
    if distance <= attack_radius:
        return 'attack'
    elif distance <= notice_radius:
        return 'move'
    else:
        return 'idle'


def e_move(e_pos, players_dict, enemies_sprites_list, enemies_physics):
    # move the enemy
    direction = get_player_distance_direction(players_dict, e_pos)[1]
    e_pos = (e_pos[0] + direction[0] * 3, e_pos[1] + direction[1] * 3)

    # check for out-of-bounds
    if e_pos[0] - 32 <= 439.8:  # left
        e_pos = 439.8, e_pos[1]
    elif e_pos[0] + 32 >= 28635.8:  # right
        e_pos = 28635.8, e_pos[1]
    elif e_pos[1] + 32 >= 19724:  # up
        e_pos = e_pos[0], 19724
    elif e_pos[1] - 32 <= 525:  # down
        e_pos = e_pos[0], 525

    # update physics
    for i, enemy_sprite in enumerate(enemies_sprites_list):
        if enemy_sprite.center == (e_pos[0], e_pos[1]):
            enemies_physics[i].update()

    return e_pos


def update_enemies(players_dict, enemies_data, enemies_names, enemies_sprites_list, enemies_physics):
    # update all the enemies
    for i, enemy_sprite in enumerate(enemies_sprites_list):
        status = get_status(enemies_data, enemy_sprite.center, enemies_names[i])
        if not status == 'attack':
            enemy_sprite.center = e_move(enemy_sprite.center, players_dict, enemies_sprites_list, enemies_physics)


# ------------------ server ------------------


def receive():
    while True:
        message, addr = receive_message(slave, private_key, public_key)
        msg_str = message.decode()
        msg_parts = msg_str.split(',')

        if msg_parts[1] == 'CHAT':
            # receiving chats
            chats.append(eval(msg_parts[2]))

        elif len(msg_parts) == 3 and msg_parts[1] == 'KILL':
            # clients log out
            username = msg_parts[2]
            for client in clients:
                if client != addr:
                    send_response(slave, f'SERVER,KILL,{username}'.encode(), public_key, private_key, client)
            if username in players_dict:
                players_dict.pop(username)
            if addr in clients:
                clients.remove(addr)

        elif len(msg_parts) == 5 and msg_parts[1] == 'PSS':
            # making players cords list
            name, x, y = msg_parts[0], msg_parts[2], msg_parts[3]
            players_dict[name] = (x, y)
            if addr not in clients:
                clients.append(addr)
            if len(clients) != 1:
                # sending clients list to new client
                clients_list = ','.join(p for p in players_dict.keys() if p != name)
                msg = f'SERVER,LOG,{clients_list}'
                send_response(slave, msg.encode(), public_key, private_key, addr)
                # sending info about new client to all clients
                for client in clients:
                    if client != addr:
                        send_response(slave, f'SERVER,LOG,{name}'.encode(), public_key, private_key, client)

        elif len(msg_parts) == 4 and msg_parts[1] == 'HURT':
            # enemies hurt :(
            index = int(msg_parts[2])
            if index < len(enemies_died) and not enemies_died[index]:
                damage = int(msg_parts[3])
                enemies_health[index] = max(0, enemies_health[index] - damage)
                if enemies_health[index] == 0:
                    enemies_died[index] = True

        elif len(msg_parts) >= 3 and msg_parts[1] in ["MDROP", "PDROP", "WAT", "MAT", "PSS", "MSG"]:
            # take care of message
            messages.put((message, addr))


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            msg_parts = message.decode().split(',')
            msg_type = msg_parts[1]

            if msg_type == "MSG":
                for chat in chats:
                    if chat != addr:
                        send_response(slave, message, public_key, private_key, chat)

            if msg_type in ["MDROP", "PDROP", "WAT", "MAT"]:
                for client in clients:
                    if addr != client or len(clients) == 1:
                        send_response(slave, message, public_key, private_key, client)

            elif msg_type == 'PSS':
                # updating enemies
                enemies()
                enemy_message = ''
                client_index = clients.index(addr)
                client_cords = players_dict[client_index]

                for index, sprite in enumerate(enemies_sprites_list):
                    cords = (sprite.center_x, sprite.center_y)
                    health = enemies_health[index]
                    status = get_status(cords, enemies_names[index])

                    if health <= 0:
                        # create enemies drops
                        drop_pos = (sprite.center_x, sprite.center_y)
                        drop_names = [choice(enemy_data[enemies_names[index]]['drop']),
                                      choice(enemy_data[enemies_names[index]]['drop'])]
                        for client in clients:
                            # drop 1
                            drop1_msg = f'SERVER,MDROP,{drop_names[0]},{drop_pos},{status}'
                            send_response(slave, drop1_msg.encode(), public_key, private_key, client)
                            # drop 2
                            drop2_msg = f'SERVER,MDROP,{drop_names[1]},{drop_pos},{status}'
                            send_response(slave, drop2_msg.encode(), public_key, private_key, client)

                        # other stuff
                        enemies_died_time[index] = time.time()
                        enemies_died[index] = True
                        sprite.center_x, sprite.center_y = (random.randint(SPAWN["left"], SPAWN["right"]),
                                                            random.randint(SPAWN["down"], SPAWN["up"]))
                        enemies_health[index] = enemy_data[enemies_names[index]]['health']
                    else:
                        # only send info about enemies near client
                        if abs(cords[0] - client_cords[0]) <= SCREEN_WIDTH and abs(
                                cords[1] - client_cords[1]) <= SCREEN_HEIGHT and not enemies_died[index]:
                            enemy_message += f',{cords},{status},{health},{index}'
                        elif enemies_died[index] and time.time() - enemies_died_time[
                            index] >= 0.3:  # after die - when revive - send info about the revivig pos
                            enemies_died[index] = False

                msg = message.decode() + enemy_message
                for client in clients:
                    send_response(slave, msg.encode(), public_key, private_key, client)


# ------------------ main ------------------
# enemies start
walls = tile_map.sprite_lists[LAYER_NAME_BARRIER]
for i in range(ENEMIES_NUM):  # setup the enemies
    if i == 0:
        name = 'Raccoon'
    elif i < ENEMIES_NUM / 4:
        name = 'Squid'
    elif i < ENEMIES_NUM / 2:
        name = 'Spirit'
    else:
        name = 'Bamboo'
    # making sprite
    enemy = Sprite(enemy_data[name]['filename'])
    enemy.center_x, enemy.center_y = (random.randint(SPAWN["left"], SPAWN["right"]), random.randint(
        SPAWN["down"],
        SPAWN["up"]))
    enemies_sprites_list.append(enemy)
    walls.append(enemy)
    # lists adding
    enemies_names.append(enemy_data[name]['layer'])
    enemies_health.append(enemy_data[name]['health'])
    enemies_died.append(False)
    enemies_died_time.append(time.time())

# physics
for sprite in enemies_sprites_list:
    walls.remove(sprite)
    physic = PhysicsEngineSimple(sprite, walls)
    enemies_physics.append(physic)
    walls.append(sprite)

while True:
    data, addr = receive_message(slave, private_key, public_key)
    if data.decode() == 'done':
        break

print('slave is up and running!')

t2 = threading.Thread(target=receive)
t3 = threading.Thread(target=broadcast)

t2.start()
t3.start()
