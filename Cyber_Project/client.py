import threading
import queue
import arcade
import time
import random
from socket import *
from settings import *
from random import choice
from player import Player
from enemy import Enemy
from weapon import Weapon
from magic import Magic
from drop import Drop
from ui_screen import UI_SCREEN
from ui import UI

# parameters for the server to use
NAME = 'CLIENT'
ADDR = (CLIENT_IP, CLIENT_PORT)
Server_ADDR = (LB_IP, LB_PORT)
messages = queue.Queue()

# setting up the server
game = socket(AF_INET, SOCK_DGRAM)
game.bind(ADDR)
game.sendto(f'IP, {ADDR}'.encode(), Server_ADDR)
while True:
    data, addr = game.recvfrom(RECV_SIZE)
    if data.decode():
        Server_ADDR = data.decode()
        Server_ADDR = eval(Server_ADDR)
        break
print("connected")


def get_info():
    while True:
        data, addr = game.recvfrom(RECV_SIZE)
        if data.decode().split(',')[1] == 'PING':
            game.sendto(f'{NAME},PONG'.encode(), Server_ADDR)
        else:
            messages.put((data, addr))


t = threading.Thread(target=get_info)
t.start()


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True, vsync=True)
        arcade.set_background_color(SCREEN_COLOR)

        # Screen
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(self.width, self.height)
        self.tile_map = arcade.load_tilemap(TILED_MAP, TILE_SIZE, layer_options=LAYER_OPTIONS)
        self.pss_msg = []
        self.pss_time = time.time()
        self.use_srgb = True

        # Sound
        self.sound = arcade.Sound(DEFAULT_MUSIC, streaming=True)
        self.volume = MUSIC_VOLUME
        self.player_sound = arcade.play_sound(self.sound, self.volume)

        # My Player
        self.player = Player(PLAYER_IMAGE, SPRITE_SCALING)
        self.player_physics_engine = None
        self.message = ''
        self.messaging = False

        # Players Communication
        self.players = {NAME: self.player, 'MALE': Player(PLAYER_IMAGE, SPRITE_SCALING), 'FEMALE': Player(PLAYER_IMAGE, SPRITE_SCALING)}
        self.player_list = arcade.SpriteList()
        self.drops_list = []
        self.drops_number = 0
        self.weapons_list = []
        self.weapons_number = 0
        self.magic_list = []
        self.magic_number = 0

        # Enemies
        self.enemies_list = []
        self.dead_enemies_list = []
        self.enemies_physics = []
        self.enemies_number = 0

        # Inventory
        self.ui_screen = UI_SCREEN(self.player)
        self.ui = UI(self.player)
        self.game_paused_ui = False
        self.selection = 'sword'

    # ------------------ set up ------------------

    def setup(self):
        # Screen
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Player
        self.player.center_x, self.player.center_y = random.randint(MAP_LEFT, MAP_RIGHT), random.randint(MAP_DOWN, MAP_UP)
        for p_name, p_sprite in self.players.items():
            if p_name != NAME: self.player_list.append(p_sprite)
        self.scene.add_sprite_list('Players', False, self.player_list)
        self.scene.add_sprite('Player', self.player)
        game.sendto(
            f'{NAME},PSS,{self.player.center_x},{self.player.center_y},{self.player.status},{self.player.health}'.encode(),
            Server_ADDR)

        # enemies
        self.draw_enemies()

        # Physics :(
        player_collisions = self.scene[LAYER_NAME_BARRIER]
        for player in self.player_list:
            if player in player_collisions:
                continue
            player_collisions.append(player)
        self.player_physics_engine = arcade.PhysicsEngineSimple(self.player, walls=player_collisions)

    def on_draw(self):
        # Clear the screen to the background color
        self.clear()

        # Draw our seen screen
        self.scene.draw()
        self.camera.use()

        # enemies health
        for monster in self.enemies_list:
            if monster.name != 'Raccoon':
                arcade.draw_text(monster.health, monster.center_x, monster.center_y + 34, arcade.color.WHITE, 14)
            else:
                arcade.draw_text(monster.health, monster.center_x, monster.center_y + 104, arcade.color.WHITE, 14)

        # players health
        for p_name, p_sprite in self.players.items():
            arcade.draw_text(p_name + "  " + str(p_sprite.health), p_sprite.center_x - 34, p_sprite.center_y + 34,
                             arcade.color.WHITE, 14)

        # inventory
        self.ui.display()
        if self.game_paused_ui:
            self.ui_screen.display(self.selection)

    def main_cooldowns(self):
        # the function name is pretty clear...
        current_time = time.time()

        if self.player.attacking:
            if current_time - self.player.attack_time >= weapon_data[self.player.weapon]['cooldown']:
                self.player.attacking = False
                self.destroy_attack()

        if self.player.magicing:
            if current_time - self.player.magic_time >= magic_data[self.player.magic]['cooldown']:
                self.player.magicing = False
                self.destroy_magic()

        for weapon in self.weapons_list:
            if current_time - weapon.time >= weapon_data[weapon.name]['cooldown']:
                weapon.kill()

        for magic in self.magic_list:
            if current_time - magic.time >= magic_data[magic.name]['cooldown']:
                magic.kill()

        if not self.player.vulnerable:
            if current_time - self.player.hurt_time >= 0.4:
                self.player.vulnerable = True

    def center_camera_to_player(self):
        # the function name is pretty clear...
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    # ------------------ key input ------------------

    def on_key_press(self, key, modifiers):
        # Don't move if attack
        if self.player.attacking or self.player.magicing or self.messaging:
            return
        # attack!
        if key == arcade.key.SPACE:
            self.create_attack()
        # magic
        elif key == arcade.key.M:
            self.create_magic()
        # auto movement
        elif key == arcade.key.P:
            self.player.auto_movement = not self.player.auto_movement
            if self.player.auto_movement is False:
                self.player.change_x, self.player.change_y = (0, 0)
        # Don't take inputs if on auto movement
        elif self.player.auto_movement:
            return
        # inputs
        elif key == arcade.key.W:
            self.player.change_y = self.player.speed
        elif key == arcade.key.S:
            self.player.change_y = -self.player.speed
        elif key == arcade.key.A:
            self.player.change_x = -self.player.speed
        elif key == arcade.key.D:
            self.player.change_x = self.player.speed

    def on_key_release(self, key, modifiers):
        # chat!
        if key == arcade.key.ENTER:
            self.messaging = not self.messaging
            # if player turned off messaging
            if not self.messaging:
                if self.message != '':
                    print(self.message, end='')
                print('\nwrite mod off')
                self.message = ''
            # if player turned on messaging
            else:
                print('write mod on')

        elif self.messaging:
            if key == arcade.key.BACKSPACE:
                self.message = self.message[:-1]
            else:
                self.message += chr(key)

        # regular movement
        elif key == arcade.key.W:
            self.player.change_y = 0
        elif key == arcade.key.S:
            self.player.change_y = 0
        elif key == arcade.key.A:
            self.player.change_x = 0
        elif key == arcade.key.D:
            self.player.change_x = 0

        # cords printing
        elif key == arcade.key.X:
            print(f'({self.player.center_x},{self.player.center_y})')

        # drops :P
        elif key == arcade.key.Q and self.player.item is not None:
            self.create_drop()
            for barrier in self.scene.get_sprite_list(LAYER_NAME_BARRIER):
                if arcade.check_for_collision(barrier, self.player.last_drop):
                    self.pick_up_drops(self.player.last_drop)
                    return

        # inventory!
        elif key == arcade.key.E:
            self.game_paused_ui = not self.game_paused_ui

        elif self.game_paused_ui:
            if key == arcade.key.RIGHT:
                self.player.selection_index += 1
                if self.player.selection_index > len(list(self.player.items.keys())) - 1:
                    self.player.selection_index = 0
                self.selection = list(self.player.items.keys())[self.player.selection_index]

            elif key == arcade.key.LEFT:
                self.player.selection_index -= 1
                if self.player.selection_index < 0:
                    self.player.selection_index = len(list(self.player.items.keys())) - 1
                self.selection = list(self.player.items.keys())[self.player.selection_index]

            elif key == arcade.key.UP:
                # weapon
                if list(self.player.items.values())[self.player.selection_index]['type'] == 'weapon':
                    self.player.weapon = list(self.player.items.keys())[self.player.selection_index]
                    self.player.current_attack = Weapon((self.player.center_x, self.player.center_y), self.player.weapon, self.player.status)

                # magic
                elif list(self.player.items.values())[self.player.selection_index]['type'] == 'magic':
                    self.player.magic = list(self.player.items.keys())[self.player.selection_index]

                # drop
                elif list(self.player.items.values())[self.player.selection_index]['type'] == 'drop':
                    self.player.item = list(self.player.items.keys())[self.player.selection_index]

    # ------------------ player ------------------

    def auto_move(self):
        # the function name is pretty clear...
        current_time = time.time()

        if current_time - self.player.auto_movement_time >= 0.4:
            self.player.auto_movement_time = time.time()
            x, y = self.player.center_x, self.player.center_y
            for barrier in self.scene.get_sprite_list(LAYER_NAME_BARRIER):
                # check if can move left
                self.player.center_x -= 64
                if arcade.check_for_collision(barrier, self.player) and (-1, 0) in self.player.movement_options:
                    self.player.movement_options.remove((-1, 0))
                self.player.center_x = x

                # check if can move right
                self.player.center_x += 64
                if arcade.check_for_collision(barrier, self.player) and (1, 0) in self.player.movement_options:
                    self.player.movement_options.remove((1, 0))
                self.player.center_x = x

                # check if can move down
                self.player.center_y -= 64
                if arcade.check_for_collision(barrier, self.player) and (0, -1) in self.player.movement_options:
                    self.player.movement_options.remove((0, -1))
                self.player.center_y = y

                # check if can move up
                self.player.center_y += 64
                if arcade.check_for_collision(barrier, self.player) and (0, 1) in self.player.movement_options:
                    self.player.movement_options.remove((0, 1))
                self.player.center_y = y

        if current_time - self.player.auto_movement_time2 >= 1.5:
            self.player.auto_movement_time2 = time.time()
            self.player.movement_options = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(self.player.movement_options)

        # Move!
        self.player.change_x, self.player.change_y = self.player.movement_options[0]
        self.player.change_x *= self.player.speed
        self.player.change_y *= self.player.speed

    def check_if_attacked(self):
        # the function name is pretty clear...
        for monster in self.enemies_list:
            if monster.attacked == self.player:
                return True
        return False

    # ------------------ enemies ------------------

    def draw_enemies(self):
        # draw
        for i in range(ENEMIES_NUM):
            if i == 0:
                name = 'Raccoon'
            elif i < ENEMIES_NUM / 4:
                name = 'Squid'
            elif i < ENEMIES_NUM / 2:
                name = 'Spirit'
            else:
                name = 'Bamboo'
            enemy = Enemy(enemy_data[name]['filename'], ENTITY_SIZE, enemy_data[name]['layer'], self.player,
                          self.player_list, self.enemies_number)

            self.enemies_number += 1
            self.enemies_list.append(enemy)

            self.scene.add_sprite(LAYER_NAME_ENTITY, enemy)

        # physics
        for monster in self.enemies_list:
            enemies_collision = self.scene[LAYER_NAME_BARRIER]
            for other_enemy in self.enemies_list:
                if other_enemy == monster:
                    continue
                if other_enemy in enemies_collision:
                    continue
                enemies_collision.append(other_enemy)

            physics = arcade.PhysicsEngineSimple(monster, walls=enemies_collision)
            self.enemies_physics.append(physics)

    def enemies_update(self):
        # movement & health & death
        if self.enemies_list:
            for monster in self.enemies_list:
                # update
                monster.e_update()

    def damage_enemies(self):
        # the function name is pretty clear...
        for index, monster in enumerate(self.enemies_list):
            if arcade.check_for_collision(self.player.current_attack, monster):
                game.sendto(f"{NAME},HURT,{index},{self.player.stats['attack']}".encode(), Server_ADDR)

    # ------------------ attack! ------------------

    def create_attack(self):
        # the function name is pretty clear...
        self.player.attack_time = time.time()
        self.player.current_attack = Weapon((self.player.center_x, self.player.center_y), self.player.weapon, self.player.status)
        self.scene.add_sprite(LAYER_NAME_ITEM, self.player.current_attack)
        self.player.attacking = True
        # WAT message
        game.sendto(
            f'{NAME},WAT,{self.player.center_x},{self.player.center_y},{self.player.status},{self.player.weapon}'.encode(),
            Server_ADDR)

    def destroy_attack(self):
        # the function name is pretty clear...
        self.player.attacking = False
        self.player.current_attack.kill()
        self.damage_enemies()

    def damage_player(self):
        # the function name is pretty clear...
        if self.player.vulnerable:
            self.player.vulnerable = False
            self.player.hurt_time = time.time()
            for monster in self.enemies_list:
                if monster.status != 'attack' or monster.attacked != self.player:
                    continue
                elif self.player.health - enemy_data[monster.name]['damage'] <= 0:
                    self.player.health = 0
                elif self.player.health > 0:
                    self.player.health -= enemy_data[monster.name]['damage']
                else:
                    self.player.health = 0

    # ------------------ magic ------------------

    def create_magic(self):
        # the function name is pretty clear...
        self.player.magic_time = time.time()
        self.player.magicing = True
        self.player.current_magic = Magic((self.player.center_x, self.player.center_y), self.player.magic, self.player.status)
        if self.player.magic == 'potion':
            arcade.stop_sound(self.player_sound)
            self.sound = arcade.Sound(POTION_MUSIC, streaming=True)
            self.player_sound = arcade.play_sound(self.sound, self.volume)
        elif self.player.magic == 'potion1':
            arcade.stop_sound(self.player_sound)
            self.sound = arcade.Sound(POTION1_MUSIC, streaming=True)
            self.player_sound = arcade.play_sound(self.sound, self.volume)
        did_magic = self.player.magic_update(self.player.current_magic)
        if not did_magic: return
        self.scene.add_sprite(LAYER_NAME_ITEM, self.player.current_magic)
        # MAT message
        game.sendto(
            f'{NAME},MAT,{self.player.current_magic.center_x},{self.player.current_magic.center_y},{self.player.status},{self.player.magic}'.encode(),
            Server_ADDR)
        # ui update
        self.player.ui_magic_update(self.ui_screen)

    def destroy_magic(self):
        # the function name is pretty clear...
        if self.player.magic == 'flame':
            for index, monster in enumerate(self.enemies_list):
                if arcade.check_for_collision(self.player.current_magic, monster):
                    game.sendto(f"{NAME},HURT,{index},{self.player.stats['attack']}".encode(), Server_ADDR)

        self.player.magicing = False
        self.player.current_magic.kill()

    # ------------------ drop ------------------

    def create_drop(self):
        # the function name is pretty clear...
        self.drops_number += 1
        drops_pos = (int(self.player.center_x), int(self.player.center_y))
        self.player.last_drop = Drop(self.player.item, drops_pos, self.player.status, self.drops_number)
        game.sendto(f'{NAME},MDROP,{self.player.item},{drops_pos},{self.player.status}'.encode(), Server_ADDR)
        self.drops_list.append(self.player.last_drop)
        self.scene.add_sprite(LAYER_NAME_ITEM, self.player.last_drop)
        # reducing amount of drop
        self.player.items[self.player.item]['amount'] -= 1
        # amount is 0, this drop is no more
        if self.player.items[self.player.item]['amount'] == 0:
            self.player.items.pop(self.player.item, None)
            self.player.item = None
            self.ui_screen.attribute_index -= 1

    def pick_up_drops(self, drop):
        # the function name is pretty clear...
        if drop.name in self.player.items.keys():
            #  increasing the amount of this drop - player pick up! :)
            self.player.items[drop.name]['amount'] += 1
        else:
            #  adding this drop to player's items list
            self.player.items[drop.name] = {}
            self.player.items[drop.name].update(drop_data[drop.name])
            self.ui_screen.attribute_index += 1
        # send info to server
        game.sendto(f'{NAME},PDROP,{drop.name},{drop.pos}'.encode(), Server_ADDR)
        # this drop is no more on the floor :(
        drop.kill()
        self.drops_number -= 1
        self.drops_list.remove(drop)

    def check_if_pick_up_drops(self):
        # the function name is pretty clear...
        for drop in self.drops_list:
            if arcade.check_for_collision(self.player, drop):
                self.pick_up_drops(drop)

    # ------------------ update ------------------

    def read_pss_msg(self):
        # Players
        name = self.pss_msg[0]
        if name not in list(self.players.keys()): return
        if name != NAME:
            other_player = self.players[name]
            cords = self.pss_msg[2], self.pss_msg[3]
            if int(float(cords[0])) != other_player.center_x or int(float(cords[1])) != other_player.center_y:
                other_player.center_x = int(float(cords[0]))
                other_player.center_y = int(float(cords[1]))
            status = self.pss_msg[4]
            if other_player.status != status:
                other_player.status = status
            health = self.pss_msg[5]
            if other_player.health != health:
                other_player.health = health

        # Enemies
        if len(self.pss_msg) < 7 or not self.enemies_list: return
        index = 6
        for enemy_list_index, enemy in enumerate(self.enemies_list):
            enemy_pkt_index = self.pss_msg[index + 4]
            if int(enemy_pkt_index) != enemy_list_index: continue

            cords = float(self.pss_msg[index][1:]), float(self.pss_msg[index + 1][1:self.pss_msg[index + 1].find(')')])
            status = self.pss_msg[index + 2]
            health = int(float(self.pss_msg[index + 3]))
            enemy.status = status
            enemy.center_x, enemy.center_y = cords
            enemy.health = health
            if index + 5 > len(self.pss_msg) - 1:
                return
            index += 5

    def send_stuff(self):
        # PSS
        pss = f'{NAME},PSS,{self.player.center_x},{self.player.center_y},{self.player.status},{self.player.health}'
        game.sendto(pss.encode(), Server_ADDR)

    def on_update(self, delta_time):
        # Music!
        if self.player_sound.time == 0:
            self.player_sound = arcade.play_sound(self.sound, self.volume)

        # Screen
        self.main_cooldowns()
        self.center_camera_to_player()

        # Players
        self.player_list.update()

        # My Player
        if not self.player.attacking and not self.player.magicing:
            self.player_physics_engine.update()
        if self.player.auto_movement:
            self.auto_move()
        if self.check_if_attacked():
            self.damage_player()
        self.player.get_status()
        self.player.update()
        if len(self.player.items.keys()) < UI_SIZE:
            self.check_if_pick_up_drops()

        # Enemies
        for physics in self.enemies_physics:
            physics.update()
        self.enemies_update()

        # Receive info
        if self.pss_msg:
            self.read_pss_msg()
        if time.time() - self.pss_time >= PSS_COOLDOWN:
            self.pss_time = time.time()
            self.send_stuff()
        if not messages.empty():
            data, addr = messages.get()
            data = data.decode().split(',')
            name = data[0]
            type = data[1]

            if type == 'PSS':
                self.pss_msg = data

            elif type == 'KILL':
                username = data[2]
                self.players[username].kill()
                self.players.pop(username)

            elif type == 'WAT' and name != NAME:
                cords = (int(float(data[2])), int(float(data[3])))
                p_status = data[4]
                weapon_name = data[5]

                self.weapons_number += 1
                weapon = Weapon(cords, weapon_name, p_status)
                weapon.time = time.time()
                self.weapons_list.append(weapon)
                self.scene.add_sprite(LAYER_NAME_ITEM, weapon)

            elif type == 'MAT' and name != NAME:
                cords = (int(float(data[2])), int(float(data[3])))
                p_status = data[4]
                magic_name = data[5]

                self.magic_number += 1
                magic = Magic(cords, magic_name, p_status)
                if magic.name in ('potion', 'potion1'):
                    magic.scale = 0.2
                magic.time = time.time()
                self.magic_list.append(magic)
                self.scene.add_sprite(LAYER_NAME_ITEM, magic)

            elif type == 'MDROP' and name != NAME:
                self.drops_number += 1
                drop_name, drop_status = data[2], data[5]
                drop_pos = (int(float(data[3][1:])),
                            int(float(data[4][1:data[4].find(')')])))
                drop = Drop(drop_name, drop_pos, drop_status, self.drops_number)
                self.drops_list.append(drop)
                self.scene.add_sprite(LAYER_NAME_ITEM, drop)

            elif type == 'PDROP' and name != NAME:
                drop_name = data[2]
                drop_pos = (int(float(data[3][1:])),
                            int(float(data[4][1:data[4].find(')')])))
                for drop in self.drops_list:
                    if drop.name != drop_name:
                        continue
                    if drop.pos == drop_pos:
                        drop.kill()
                        self.drops_number -= 1
                        self.drops_list.remove(drop)


# game
window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, NAME)
window.setup()
arcade.run()
game.close()