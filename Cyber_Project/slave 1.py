from socket import *
from settings import *
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
clients = []
messages = queue.Queue()

# setting up the server
slave = socket(AF_INET, SOCK_DGRAM)
slave.bind(ADDR)
slave.sendto(f'{ADDR}'.encode(), (LB_IP, LB_PORT))

# Game
players_dict = {'MALE': (0, 0), 'FEMALE': (0, 0)}
enemies_number = 0
enemies_cords = []
enemies_names = []
enemies_health = []
enemies_died = []
enemies_died_time = []
enemies_movement_options = []
auto_move_time = []
auto_move_time2 = []
layer_options = {
    LAYER_NAME_ENTITY: {"use_spatial_hash": True}}
tile_map = arcade.load_tilemap(TILED_MAP, TILE_SIZE, layer_options=layer_options)


# ------------------ enemies ------------------
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


def enemies_auto_move(index):
    if time.time() - auto_move_time[index] >= 0.4:
        auto_move_time[index] = time.time()
        if enemies_cords[index][0] - 64 <= 1000 and (-1, 0) in enemies_movement_options[index]:  # left, 439.8
            enemies_movement_options[index].remove((-1, 0))

        elif enemies_cords[index][0] + 64 >= 1000 and (1, 0) in enemies_movement_options[index]:  # right, 28635.8
            enemies_movement_options[index].remove((1, 0))

        elif enemies_cords[index][1] - 64 <= 500 and (0, -1) in enemies_movement_options[index]:  # down, 525
            enemies_movement_options[index].remove((0, -1))

        elif enemies_cords[index][1] + 64 >= 1800 and (0, 1) in enemies_movement_options[index]:  # up, 19724
            enemies_movement_options[index].remove((0, 1))

    if time.time() - auto_move_time2[index] >= 1.5:
        auto_move_time2[index] = time.time()
        enemies_movement_options[index] = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(enemies_movement_options[index])

    # Move!
    return (enemies_cords[index][0] + enemies_movement_options[index][0][0],
            enemies_cords[index][1] + enemies_movement_options[index][0][1])


def e_move(e_pos):
    # move
    e_pos = e_pos[0] + get_player_distance_direction(e_pos)[1][0], e_pos[1] + get_player_distance_direction(e_pos)[1][1]

    if e_pos[0] - 32 <= 439.8:  # left
        e_pos = 439.8, e_pos[1]
    elif e_pos[0] + 32 >= 28635.8:  # right
        e_pos = 28635.8, e_pos[1]
    elif e_pos[1] + 32 >= 19724:  # up
        e_pos = e_pos[0], 19724
    elif e_pos[1] - 32 <= 525:  # down
        e_pos = e_pos[0], 525

    return e_pos


def enemies():
    # enemies update
    for index, e_pos in enumerate(enemies_cords):
        status = get_status(e_pos, enemies_names[index])
        if status == 'idle':
            enemies_cords[index] = enemies_auto_move(index)
        elif status == 'move':
            enemies_cords[index] = e_move(e_pos)

# ------------------ server ------------------


def receive():
    while True:
        message, addr = slave.recvfrom(RECV_SIZE)

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
            #enemies_cords[index] = enemies_cords[index][0] - 64,  enemies_cords[index][1] - 64
        # take care of message
        messages.put((message, addr))


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            for client_index, client in enumerate(clients):
                if addr == client:
                    continue
                if message.decode().split(',')[1] == 'HURT':
                    continue
                if message.decode().split(',')[1] == 'PSS':
                    enemies()
                    enemy_message = ''
                    for index, cords in enumerate(enemies_cords):
                        health = enemies_health[index]
                        status = get_status(cords, enemies_names[index])
                        client_cords = list(players_dict.values())[client_index]
                        get_to_list_conditions = ((abs(float(cords[0]) - float(client_cords[0])) <= SCREEN_WIDTH//2 and
                                                  abs(float(cords[1]) - float(client_cords[1])) <= SCREEN_HEIGHT//2) or
                                                  enemies_died[index])

                        if get_to_list_conditions:
                            enemy_message += f',{cords},{status},{health},{index}'
                            if enemies_died[index] and time.time() - enemies_died_time[index] >= 0.3:
                                enemies_died[index] = False

                        if health <= 0:
                            enemies_died_time[index] = time.time()
                            enemies_died[index] = True
                            enemies_cords[index] = (
                                choice(tile_map.sprite_lists[LAYER_NAME_ENTITY]).center_x,
                                choice(tile_map.sprite_lists[LAYER_NAME_ENTITY]).center_y)
                            enemies_health[index] = enemy_data[enemies_names[index]]['health']

                    msg = message.decode()+enemy_message
                    slave.sendto(f'{msg}'.encode(), client)
                elif message.decode().split(',')[1] in ["TDROP", "PDROP", "WAT", "MAT"]:
                    slave.sendto(f'{message.decode()}'.encode(), client)


def find_clients():
    while True:
        data, addr = slave.recvfrom(RECV_SIZE)
        if data.decode():
            the_data = data.decode()
            if the_data[0:2] == 'IP':
                clients.append(eval(the_data[2:]))
                if len(clients) == 2:
                    break

# ------------------ main ------------------


def main():
    # enemies start
    for monster in tile_map.sprite_lists[LAYER_NAME_ENTITY]:
        enemies_cords.append((monster.center_x, monster.center_y))
        enemies_names.append(enemy_data['Squid']['layer'])
        enemies_health.append(enemy_data['Squid']['health'])
        enemies_died.append(False)
        enemies_died_time.append(time.time())
        enemies_movement_options.append([(0, 1), (0, -1), (1, 0), (-1, 0)])
        auto_move_time.append(time.time())
        auto_move_time2.append(time.time())

    while True:
        data, addr = slave.recvfrom(RECV_SIZE)
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


if __name__ == "__main__":
    main()
