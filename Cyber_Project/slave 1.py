from socket import *
from settings import *
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from random import choice
import arcade
import queue
import threading
import math
import time
import random

# parameters for the server to use
HOST = S1_IP
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


def load_public_key(filename):
    with open(filename, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key


def receive_message(server_socket, private_key, public_key):
    data, client_address = server_socket.recvfrom(RECV_SIZE)
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
        exit()
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


# Load the private key from the PEM encoded file
private_key = load_private_key("private_key.pem")
# Load the public key from the PEM encoded file
public_key = load_public_key("public_key.pem")
# setting up the server
slave = socket(AF_INET, SOCK_DGRAM)
slave.bind(ADDR)
send_response(slave, f'{ADDR}'.encode(), public_key, private_key, (LB_IP, LB_PORT))

# Game
layer_options = {LAYER_NAME_BARRIER: {"use_spatial_hash": True}}
tile_map = arcade.load_tilemap(TILED_MAP, TILE_SIZE, layer_options=layer_options)
players_dict = {}
enemies_sprites_list = []
enemies_physics = []
enemies_names = []
enemies_health = []
enemies_died = []
enemies_died_time = []


# ------------------ enemies ------------------
def get_player_distance_direction(e_pos):
    # the function name is pretty clear...
    p_cords = list(players_dict.values())
    min_distance_vec = (float(p_cords[0][0]) - float(e_pos[0]), float(p_cords[0][1]) - float(e_pos[1]))
    min_distance = math.sqrt((min_distance_vec[0]) ** 2 + (min_distance_vec[1]) ** 2)

    for player in p_cords:
        distance_vec = (float(player[0]) - float(e_pos[0]), float(player[1]) - float(e_pos[1]))
        distance = math.sqrt((distance_vec[0]) ** 2 + (distance_vec[1]) ** 2)
        if min_distance > distance:
            min_distance_vec = distance_vec
            min_distance = distance

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


def get_status(e_pos, name):
    # the function name is pretty clear...
    distance = get_player_distance_direction(e_pos)[0]
    notice_radius = enemy_data[name]['notice_radius']
    attack_radius = enemy_data[name]['attack_radius']
    if distance <= attack_radius:
        return 'attack'
    elif distance <= notice_radius:
        return 'move'
    else:
        return 'idle'


def e_move(sprite):
    # move
    e_pos = sprite.center_x, sprite.center_y
    e_pos = (e_pos[0] + get_player_distance_direction(e_pos)[1][0]*3,
             e_pos[1] + get_player_distance_direction(e_pos)[1][1]*3)

    if e_pos[0] - 32 <= 439.8:  # left
        e_pos = 439.8, e_pos[1]
    elif e_pos[0] + 32 >= 28635.8:  # right
        e_pos = 28635.8, e_pos[1]
    elif e_pos[1] + 32 >= 19724:  # up
        e_pos = e_pos[0], 19724
    elif e_pos[1] - 32 <= 525:  # down
        e_pos = e_pos[0], 525

    # Check for out-of-bounds
    if sprite.left < MAP_LEFT:
        sprite.left = 0
    if sprite.bottom < MAP_DOWN:
        sprite.bottom = 0

    return e_pos


def enemies():
    # enemies update
    for index, sprite in enumerate(enemies_sprites_list):
        status = get_status((sprite.center_x, sprite.center_y), enemies_names[index])
        enemies_physics[index].update()
        if not status == 'attack':
            sprite.center_x, sprite.center_y = e_move(sprite)


# ------------------ server ------------------


def receive():
    while True:
        message, addr = receive_message(slave, private_key, public_key)

        # receiving clients
        if message.decode()[0:2] == 'IP':
            clients.append(eval(message.decode()[2:]))

        elif message.decode()[0:4] == 'CHAT':
            chats.append(eval(message.decode()[5:]))

        elif message.decode().split(',')[1] == "KILL":
            for client_index, client in enumerate(clients):
                username = message.decode().split(',')[0]
                print(f'{username} is no more')
                send_response(slave, f'SERVER,KILL,{username}'.encode(), public_key, private_key, client)
                if client_index == len(clients) - 1:
                    players_dict.pop(username)
                    clients.remove(addr)

        # making players cords list
        elif message.decode().split(',')[1] == "PSS":
            name = message.decode().split(',')[0]
            if name in players_dict.keys():
                players_dict[name] = (message.decode().split(',')[2], message.decode().split(',')[3])
            else:
                # new client!
                # update players dict of slave
                players_dict.update({name: (message.decode().split(',')[2], message.decode().split(',')[3])})
                if len(clients) != 1:
                    # sending clients list to new client
                    msg = f'SERVER,LOG'
                    for player_name in list(players_dict.keys()):
                        if player_name == name: continue
                        msg += f',{player_name}'
                    send_response(slave, msg.encode(), public_key, private_key, addr)
                    # sending info about new client to all clients
                    for client in clients:
                        if client == addr: continue
                        send_response(slave, f'SERVER,LOG,{name}'.encode(), public_key, private_key, client)

        # enemies hurt :(
        elif message.decode().split(',')[1] == "HURT":
            index = int(message.decode().split(',')[2])
            if enemies_died[index]: continue
            damage = int(message.decode().split(',')[3])
            if enemies_health[index] - damage <= 0:
                enemies_health[index] = 0
            elif enemies_health[index] > 0:
                enemies_health[index] -= damage
            else:
                enemies_health[index] = 0

        # take care of message
        if message.decode().split(',')[1] in ["MDROP", "PDROP", "WAT", "MAT", "PSS", "MSG"]:
            messages.put((message, addr))


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            if message.decode().split(',')[1] == "MSG":
                for chat in chats:
                    if chat == addr: continue
                    send_response(slave, message, public_key, private_key, chat)

            for client_index, client in enumerate(clients):
                # prevent errors
                if len(clients) != len(list(players_dict.keys())): continue
                # don't send pkts from client to the same client
                if addr == client and len(clients) != 1:
                    continue
                # acceptable pkt types
                if message.decode().split(',')[1] in ["MDROP", "PDROP", "WAT", "MAT"]:
                    send_response(slave, message, public_key, private_key, client)
                # pss pks type - players and enemies info
                elif message.decode().split(',')[1] == 'PSS':
                    # updating enemies
                    enemies()
                    # making info msg about enemies
                    enemy_message = ''
                    for index, sprite in enumerate(enemies_sprites_list):
                        cords = (sprite.center_x, sprite.center_y)
                        health = enemies_health[index]
                        status = get_status(cords, enemies_names[index])
                        # prevent errors
                        if len(list(players_dict.keys())) == client_index: continue
                        client_cords = list(players_dict.values())[client_index]
                        get_to_list_conditions = ((abs(float(cords[0]) - float(client_cords[0])) <= SCREEN_WIDTH and
                                                  abs(float(cords[1]) - float(client_cords[1])) <= SCREEN_HEIGHT) or
                                                  enemies_died[index])
                        # only send info about enemies near client
                        if get_to_list_conditions:
                            enemy_message += f',{cords},{status},{health},{index}'
                            if enemies_died[index] and time.time() - enemies_died_time[index] >= 0.3:  # after die - when revive - send info about the revivig pos
                                enemies_died[index] = False

                        # death! and revive...
                        if health <= 0:
                            # create enemies drops
                            drop_pos = (enemies_sprites_list[index].center_x, enemies_sprites_list[index].center_y)
                            drop_names = [choice(enemy_data[enemies_names[index]]['drop']),
                                          choice(enemy_data[enemies_names[index]]['drop'])]
                            for loop_client in clients:
                                # drop 1
                                drop1_msg = f'SERVER,MDROP,{drop_names[0]},{drop_pos},{status}'
                                send_response(slave, drop1_msg.encode(), public_key, private_key, loop_client)
                                # drop 2
                                drop2_msg = f'SERVER,MDROP,{drop_names[1]},{drop_pos},{status}'
                                send_response(slave, drop2_msg.encode(), public_key, private_key, loop_client)

                            # other stuff
                            enemies_died_time[index] = time.time()
                            enemies_died[index] = True
                            enemies_sprites_list[index].center_x, enemies_sprites_list[index].center_y = (
                            random.randint(SPAWN["left"], SPAWN["right"]), random.randint(
                                SPAWN["down"],
                                SPAWN["up"]))
                            enemies_health[index] = enemy_data[enemies_names[index]]['health']

                    # actually sending the info
                    msg = message.decode()+enemy_message
                    send_response(slave, f'{msg}'.encode(), public_key, private_key, client)


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
    enemy = arcade.Sprite(enemy_data[name]['filename'])
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
    physic = arcade.PhysicsEngineSimple(sprite, walls)
    enemies_physics.append(physic)
    walls.append(sprite)

while True:
    data, addr = receive_message(slave, private_key, public_key)
    if data.decode() == 'done':
        break

print('slave is up and running!')

# t1 = threading.Thread(target=find_clients)
t2 = threading.Thread(target=receive)
t3 = threading.Thread(target=broadcast)

# t1.start()
t2.start()
t3.start()



