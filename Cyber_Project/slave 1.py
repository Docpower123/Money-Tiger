from socket import *
from settings import *
from random import choice
import queue
import threading
import math
import time
import random

# parameters for the server to use
HOST = S1_IP
PORT = S1_PORT
ADDR = (HOST, PORT)
PING_PONG_COOLDOWN = 300000
clients = []
messages = queue.Queue()
ping_pong_time = [time.time()]
ping_pong = [False]
pong_clients = []
clients_to_kill = []

# setting up the server
slave = socket(AF_INET, SOCK_DGRAM)
slave.bind(ADDR)
slave.sendto(f'{ADDR}'.encode(), (LB_IP, LB_PORT))

# Game
players_dict = {}
enemies_cords = []
enemies_names = []
enemies_health = []
enemies_died = []
enemies_died_time = []
enemies_movement_options = []
auto_move_time = []
auto_move_time2 = []


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
        if not status == 'attack':
            enemies_cords[index] = e_move(e_pos)


# ------------------ server ------------------


def receive():
    while True:
        message, addr = slave.recvfrom(RECV_SIZE)

        if ping_pong[0]:
            # get pong packets
            if message.decode().split(',')[1] == "PONG":
                pong_clients.append(addr)
            # kill clients who do not pong
            if time.time() - ping_pong_time[0] >= PING_PONG_COOLDOWN:
                for client_index, client in enumerate(clients):
                    ping_pong[0] = False
                    if client not in pong_clients:
                        clients_to_kill.append(client)

        # receiving clients
        if message.decode()[0:2] == 'IP':
            clients.append(eval(message.decode()[2:]))

        # making players cords list
        elif message.decode().split(',')[1] == "PSS":
            name = message.decode().split(',')[0]
            if name in players_dict.keys():
                players_dict[name] = (message.decode().split(',')[2], message.decode().split(',')[3])
            else:
                players_dict.update({name: (message.decode().split(',')[2], message.decode().split(',')[3])})

        # enemies hurt :(
        elif message.decode().split(',')[1] == "HURT":
            index = int(message.decode().split(',')[2])
            damage = int(message.decode().split(',')[3])
            enemies_health[index] -= damage

        # take care of message
        if message.decode().split(',')[1] in ["MDROP", "PDROP", "WAT", "MAT", "PSS"]:
            messages.put((message, addr))


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            for client_index, client in enumerate(clients):
                # ping pong!
                if time.time() - ping_pong_time[0] >= PING_PONG_COOLDOWN:
                    slave.sendto(f'SERVER,PING'.encode(), client)
                    ping_pong_time[0] = time.time()
                    ping_pong[0] = True
                # kill clients who don't pong
                for client_to_kill in clients_to_kill:
                    username = list(players_dict.keys())[clients.index(client_to_kill)]
                    print(username, client)
                    slave.sendto(f'SERVER,KILL,{username}'.encode(), client)
                    players_dict.pop(username)
                    clients.remove(client_to_kill)
                    clients_to_kill.remove(client_to_kill)

                # don't send pkts from client to the same client
                if addr == client and len(clients) != 1:
                    continue
                # acceptable pkt types
                elif message.decode().split(',')[1] in ["MDROP", "PDROP", "WAT", "MAT"]:
                    slave.sendto(f'{message.decode()}'.encode(), client)
                # pss pks type - players and enemies info
                elif message.decode().split(',')[1] == 'PSS':
                    # updating enemies
                    enemies()
                    # prevent errors
                    if len(clients) != len(list(players_dict.keys())): break
                    # making info msg about enemies
                    enemy_message = ''
                    for index, cords in enumerate(enemies_cords):
                        health = enemies_health[index]
                        status = get_status(cords, enemies_names[index])
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
                            drop_pos = enemies_cords[index]
                            drop_names = [choice(enemy_data[enemies_names[index]]['drop']),
                                          choice(enemy_data[enemies_names[index]]['drop'])]
                            for loop_client in clients:
                                # drop 1
                                slave.sendto(f'SERVER,MDROP,{drop_names[0]},{drop_pos},{status}'.encode(), loop_client)
                                # drop 2
                                slave.sendto(f'SERVER,MDROP,{drop_names[1]},{drop_pos},{status}'.encode(), loop_client)

                            # other stuff
                            enemies_died_time[index] = time.time()
                            enemies_died[index] = True
                            enemies_cords[index] = (
                                random.randint(MAP_LEFT, MAP_RIGHT),
                                random.randint(MAP_DOWN, MAP_UP))
                            enemies_health[index] = enemy_data[enemies_names[index]]['health']

                    # actually sending the info
                    msg = message.decode()+enemy_message
                    slave.sendto(f'{msg}'.encode(), client)


# ------------------ main ------------------
# enemies start
for i in range(ENEMIES_NUM):  # setup the enemies
    if i == 0:
        name = 'Raccoon'
    elif i < ENEMIES_NUM / 4:
        name = 'Squid'
    elif i < ENEMIES_NUM / 2:
        name = 'Spirit'
    else:
        name = 'Bamboo'
    enemies_cords.append((random.randint(MAP_LEFT, MAP_RIGHT), random.randint(MAP_DOWN, MAP_UP)))
    enemies_names.append(enemy_data[name]['layer'])
    enemies_health.append(enemy_data[name]['health'])
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

# t1 = threading.Thread(target=find_clients)
t2 = threading.Thread(target=receive)
t3 = threading.Thread(target=broadcast)

# t1.start()
t2.start()
t3.start()



