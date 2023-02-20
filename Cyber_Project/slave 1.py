from socket import *
from settings import *
from enemy import Enemy
import arcade
import queue
import threading

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

# Screen
scene = arcade.Scene()
#tile_map = arcade.load_tilemap(TILED_MAP, TILE_SIZE, layer_options=LAYER_OPTIONS)

# Enemies
enemies_list = []
dead_enemies_list = []
enemies_physics = []
enemies_number = 0


def draw_enemies():
    for monster_data in enemy_data.values():
        for monster in tile_map.sprite_lists[monster_data['layer']]:
            enemy = Enemy(monster_data['filename'], ENTITY_SIZE, monster_data['layer'], player,
                          player_list, enemies_number)
            enemy.center_x, enemy.center_y = monster.center_x, monster.center_y

            enemies_number += 1
            enemies_list.append(enemy)
            try:
                enemies_collision = scene[LAYER_NAME_BARRIER].append(self.player)
            except:
                enemies_collision = scene[LAYER_NAME_BARRIER]
            physics = arcade.PhysicsEngineSimple(enemy, walls=enemies_collision)
            enemies_physics.append(physics)

            scene.add_sprite(LAYER_NAME_ENEMY, enemy)


def receive():
    while True:
        message, addr = slave.recvfrom(1024)
        messages.put((message, addr))


def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            for client in clients:
                if addr == client: continue
                print(enemies_list)
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

#draw_enemies()
find_clients()

#t1 = threading.Thread(target=find_clients)
t2 = threading.Thread(target=receive)
t3 = threading.Thread(target=broadcast)

#t1.start()
t2.start()
t3.start()

