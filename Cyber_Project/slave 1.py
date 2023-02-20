from socket import *
from settings import *
import arcade
import queue
import threading
import math

# parameters for the server to use
HOST = S1_IP
PORT = S1_PORT
ADDR = (HOST, PORT)
clients = []
messages = queue.Queue()

# setting up the server
slave = socket(AF_INET, SOCK_DGRAM)
slave.bind(ADDR)
slave.sendto(f'{ADDR}'.encode(), (LB_IP, LB_PORT))

# Game
players_dict = {}
enemies_number = 0
enemies_cords = []
enemies_names = []
enemies_health = []
tile_map = arcade.load_tilemap(TILED_MAP, TILE_SIZE, layer_options=LAYER_OPTIONS)

# enemies start
for monster_data in enemy_data.values():
    for monster in tile_map.sprite_lists[monster_data['layer']]:
        center_x, center_y = monster.center_x, monster.center_y
        enemies_number += 1
        enemies_cords.append((center_x, center_y))
        enemies_names.append(monster_data['layer'])
        enemies_health.append(monster_data['health'])


def get_player_distance_direction(e_pos):
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
    distance = get_player_distance_direction(e_pos)[0]
    notice_radius = enemy_data[name]['notice_radius']
    attack_radius = enemy_data[name]['attack_radius']
    if distance <= attack_radius:
        return 'attack'
    elif distance <= notice_radius:
        return 'move'
    else:
        return 'idle'


def e_move(e_pos):
    # move
    e_pos = e_pos[0] + get_player_distance_direction(e_pos)[1][0], e_pos[1] + get_player_distance_direction(e_pos)[1][1]
    return e_pos


def enemies():
    # enemies update
    for index, e_pos in enumerate(enemies_cords):
        if get_status(e_pos, enemies_names[index]) == 'move':
            enemies_cords[index] = e_move(e_pos)


def receive():
    while True:
        message, addr = slave.recvfrom(1024)

        # making players cords list
        if message.decode().split(',')[1] == "PSS":
            name = message.decode().split(',')[0]
            if name in players_dict.keys():
                players_dict[name] = (message.decode().split(',')[2], message.decode().split(',')[3])
            else:
                players_dict.update({name: (message.decode().split(',')[2], message.decode().split(',')[3])})
        # enemies hurt :(
        if message.decode().split(',')[1] == "HURT":
            index = int(message.decode().split(',')[2])
            damage = int(message.decode().split(',')[3])
            enemies_health[index] -= damage
            enemies_cords[index] = enemies_cords[index][0] - 64,  enemies_cords[index][1] - 64
        # take care of message
        messages.put((message, addr))


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            for client in clients:
                if addr == client: continue
                if message.decode().split(',')[1] == 'HURT': continue
                enemies()
                # send enemies cords
                enemy_message = f'SERVER,EPOS'
                for index, cords in enumerate(enemies_cords):
                    health = enemies_health[index]
                    enemy_message += f',{cords},{health}'
                slave.sendto(f'{enemy_message}'.encode(), client)
                # send from client to client
                slave.sendto(f'{message.decode()}'.encode(), client)


def find_clients():
    while True:
        data, addr = slave.recvfrom(1024)
        if data.decode():
            the_data = data.decode()
            if the_data[0:2] == 'IP':
                clients.append(eval(the_data[2:]))
                if len(clients) == 2:
                    break


while True:
    data, addr = slave.recvfrom(1024)
    if data.decode() == 'done':
        break

print('slave is up and running!')

find_clients()

# t1 = threading.Thread(target=find_clients)
t3 = threading.Thread(target=broadcast)
t2 = threading.Thread(target=receive)

# t1.start()
t2.start()
t3.start()
