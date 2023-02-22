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
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

with open('public.pem', 'rb') as f:  # Open file in binary mode
    key_bytes = f.read()

# Load the public key from the bytes using the PEM format
public_key = serialization.load_pem_public_key(key_bytes)


def encyrpt_data(info):
    # Encrypt data using the public key
    data = info.encode()
    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data


def decrypt_data(info):
    # The decryption code should use a private key, not the public key bytes
    with open('private.pem', 'rb') as f:
        private_key_bytes = f.read()
        private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    decrypted_data = private_key.decrypt(
        info,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data.decode()


# parameters for the server to use
NAME = 'MALE'
ADDR = (MALE_IP, MALE_PORT)
Server_ADDR = (LB_IP, LB_PORT)

# setting up the server
game = socket(AF_INET, SOCK_DGRAM)
game.bind(ADDR)
game.sendto(f'IP, {ADDR}'.encode(), Server_ADDR)
while True:
    data, addr = game.recvfrom(1024)
    if data.decode():
        Server_ADDR = data.decode()
        Server_ADDR = eval(Server_ADDR)
        break
print("connected")


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(SCREEN_COLOR)

        # Screen
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(self.width, self.height)
        self.tile_map = arcade.load_tilemap(TILED_MAP, TILE_SIZE, layer_options=LAYER_OPTIONS)
        print("map is good")
        self.pss_msg = []

        # My Player
        self.player = Player(PLAYER_IMAGE, SPRITE_SCALING)
        self.player_physics_engine = None
        self.message = ''
        self.messaging = False

        # Players Communication
        self.player1 = Player(PLAYER_IMAGE, SPRITE_SCALING)
        self.players = {NAME: self.player, 'FEMALE': self.player1}
        self.player_list = arcade.SpriteList()
        self.drops_list = []
        self.drops_number = 0

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
        player_x = self.tile_map.sprite_lists[LAYER_NAME_PLAYER][0].center_x
        player_y = self.tile_map.sprite_lists[LAYER_NAME_PLAYER][0].center_y
        self.player.center_x, self.player.center_y = (player_x, player_y)
        self.player_list.append(self.player1)
        self.scene.add_sprite_list('Players', False, self.player_list)
        self.scene.add_sprite('Player', self.player)

        # enemies
        self.draw_enemies()

        # Physics :(
        player_collisions = self.scene[LAYER_NAME_BARRIER]
        for player in self.player_list:
            if player in player_collisions: continue
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
        arcade.draw_text(NAME + "  " + str(self.player.health), self.player.center_x - 34, self.player.center_y + 34,
                         arcade.color.WHITE, 14)
        arcade.draw_text("FEMALE  " + str(self.player1.health), self.player1.center_x - 34, self.player1.center_y + 34,
                         arcade.color.WHITE, 14)

        # inventory
        self.ui.display()
        if self.game_paused_ui:
            self.ui_screen.display(self.selection)

    def main_cooldowns(self):
        current_time = time.time()

        if self.player.attacking:
            if current_time - self.player.attack_time >= weapon_data[self.player.weapon]['cooldown']:
                self.player.attacking = False
                self.destroy_attack()

        if not self.player.vulnerable:
            if current_time - self.player.hurt_time >= 0.4:
                self.player.vulnerable = True

    def center_camera_to_player(self):
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

        # magic! 0-0
        elif key == arcade.key.M and self.player.current_magic and self.player.magicing:
            self.destroy_magic()

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
                    self.player.current_attack = Weapon(self.player)

                # magic
                elif list(self.player.items.values())[self.player.selection_index]['type'] == 'magic':
                    self.player.magic = list(self.player.items.keys())[self.player.selection_index]

                # drop
                elif list(self.player.items.values())[self.player.selection_index]['type'] == 'drop':
                    self.player.item = list(self.player.items.keys())[self.player.selection_index]

    # ------------------ player ------------------

    def auto_move(self):
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

    def check_if_attacked(self):
        for monster in self.enemies_list:
            if monster.attacked == self.player: return True
        return False

    # ------------------ enemies ------------------

    def draw_enemies(self):
        # draw
        for monster_data in enemy_data.values():
            for monster in self.tile_map.sprite_lists[monster_data['layer']]:
                enemy = Enemy(monster_data['filename'], ENTITY_SIZE, monster_data['layer'], self.player,
                              self.player_list, self.enemies_number)

                self.enemies_number += 1
                self.enemies_list.append(enemy)

                self.scene.add_sprite(LAYER_NAME_ENEMY, enemy)

        # physics
        for monster in self.enemies_list:
            enemies_collision = self.scene[LAYER_NAME_BARRIER]
            for other_enemy in self.enemies_list:
                if other_enemy == monster: continue
                if other_enemy in enemies_collision: continue
                enemies_collision.append(other_enemy)

            physics = arcade.PhysicsEngineSimple(monster, walls=enemies_collision)
            self.enemies_physics.append(physics)

    def revive_enemies(self):
        for monster in self.dead_enemies_list:
            self.enemies_number += 1
            self.enemies_list.append(monster)
            self.dead_enemies_list.remove(monster)
            monster.center_x = choice(self.tile_map.sprite_lists[enemy_data[monster.name]['layer']]).center_x
            monster.center_y = choice(self.tile_map.sprite_lists[enemy_data[monster.name]['layer']]).center_y
            monster.health = enemy_data[monster.name]['health']
            self.scene.add_sprite(LAYER_NAME_ENEMY, monster)

    def enemy_create_drop(self, monster):
        # drop 1
        self.drops_number += 1
        drop_name = choice(enemy_data[monster.name]['drop'])
        drop_pos = (monster.center_x, monster.center_y)
        drop1 = Drop(drop_name, drop_pos, monster.status, self.drops_number)
        game.sendto(f'{NAME},TDROP,{drop_name},{drop_pos},{monster.status}'.encode(), Server_ADDR)
        self.drops_list.append(drop1)
        self.scene.add_sprite(LAYER_NAME_DROP, drop1)

        # drop 2
        self.drops_number += 1
        drop_name = choice(enemy_data[monster.name]['drop'])
        drop_pos = (monster.center_x, monster.center_y)
        drop2 = Drop(drop_name, drop_pos, monster.status, self.drops_number)
        game.sendto(f'{NAME},TDROP,{drop_name},{drop_pos},{monster.status}'.encode(), Server_ADDR)
        self.drops_list.append(drop2)
        self.scene.add_sprite(LAYER_NAME_DROP, drop2)

    def enemies_update(self):
        # movement & health & death
        if self.enemies_list:
            for monster in self.enemies_list:
                # update
                monster.e_update()
                # death!
                if monster.health <= 0:
                    # drop
                    self.enemy_create_drop(monster)

    def enemies_auto_move(self, monster):
        if time.time() - monster.auto_movement_time >= 0.4:
            monster.auto_movement_time = time.time()
            if monster.center_x - 64 <= 439.8 and (-1, 0) in monster.movement_options:  # left
                monster.movement_options.remove((-1, 0))

            elif monster.center_x + 64 >= 28635.8 and (1, 0) in monster.movement_options:  # right
                monster.movement_options.remove((1, 0))

            elif monster.center_y - 64 <= 525 and (0, -1) in monster.movement_options:  # down
                monster.movement_options.remove((0, -1))

            elif monster.center_y + 64 >= 19724 and (0, 1) in monster.movement_options:  # up
                monster.movement_options.remove((0, 1))

        if time.time() - monster.auto_movement_time2 >= 1.5:
            monster.auto_movement_time2 = time.time()
            monster.movement_options = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(monster.movement_options)

        # Move!
        monster.change_x, monster.change_y = monster.movement_options[0]

    def damage_enemies(self):
        for index, monster in enumerate(self.enemies_list):
            if arcade.check_for_collision(self.player.current_attack, monster):
                game.sendto(f"{NAME},HURT,{index},{self.player.stats['attack']}".encode(), Server_ADDR)
                if self.player.current_attack.direction == 'up':
                    direction = (0, 1)
                elif self.player.current_attack.direction == 'down':
                    direction = (0, -1)
                elif self.player.current_attack.direction == 'right':
                    direction = (1, 0)
                else:
                    direction = (-1, 0)

    # ------------------ attack! ------------------

    def create_attack(self):
        self.player.attack_time = time.time()
        self.player.current_attack = Weapon(self.player)
        self.scene.add_sprite(LAYER_NAME_WEAPON, self.player.current_attack)
        self.player.attacking = True

    def destroy_attack(self):
        self.player.attacking = False
        self.player.current_attack.kill()
        self.damage_enemies()

    def damage_player(self):
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
        self.player.magic_time = time.time()
        self.player.magicing = True
        self.player.current_magic = Magic(self.player)
        if self.player.magic == 'potion':
            arcade.stop_sound(self.player_sound)
            self.sound = arcade.Sound(POTION_MUSIC, streaming=True)
            self.player_sound = arcade.play_sound(self.sound, self.volume)
        elif self.player.magic == 'potion1':
            arcade.stop_sound(self.player_sound)
            self.sound = arcade.Sound(POTION1_MUSIC, streaming=True)
            self.player_sound = arcade.play_sound(self.sound, self.volume)
        self.player.current_magic.magic_update(self.ui_screen)
        self.scene.add_sprite(LAYER_NAME_MAGIC, self.player.current_magic)

    def destroy_magic(self):
        self.player.magicing = False
        self.player.current_magic.kill()

        if self.player.magic == 'flame':
            for monster in self.enemies_list:
                if arcade.check_for_collision(self.player.current_magic, monster):
                    monster.health -= self.player.stats['attack']

    # ------------------ drop ------------------

    def create_drop(self):
        self.drops_number += 1
        drops_pos = (self.player.center_x, self.player.center_y)
        self.player.last_drop = Drop(self.player.item, drops_pos, self.player.status, self.drops_number)
        game.sendto(f'{NAME},TDROP,{self.player.item},{drops_pos},{self.player.status}'.encode(), Server_ADDR)
        self.drops_list.append(self.player.last_drop)
        self.scene.add_sprite(LAYER_NAME_DROP, self.player.last_drop)
        # reducing amount of drop
        self.player.items[self.player.item]['amount'] -= 1
        # amount is 0, this drop is no more
        if self.player.items[self.player.item]['amount'] == 0:
            self.player.items.pop(self.player.item, None)
            self.player.item = None
            self.ui_screen.attribute_index -= 1

    def pick_up_drops(self, drop):
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
        for drop in self.drops_list:
            if arcade.check_for_collision(self.player, drop):
                self.pick_up_drops(drop)

    # ------------------ update ------------------

    def read_pss_msg(self):
        # Players
        cords = self.pss_msg[2], self.pss_msg[3]
        if int(float(cords[0])) != self.player1.center_x or int(float(cords[1])) != self.player1.center_y:
            self.player1.center_x = int(float(cords[0]))
            self.player1.center_y = int(float(cords[1]))
        status = self.pss_msg[4]
        if self.player1.status != status:
            self.player1.status = status
        health = self.pss_msg[5]
        if self.player1.health != health:
            self.player1.health = health

        # Enemies
        if len(self.pss_msg) < 7 or not self.enemies_list: return
        index = 6
        for enemy in self.enemies_list:
            cords = float(self.pss_msg[index][1:]), float(self.pss_msg[index + 1][1:self.pss_msg[index + 1].find(')')])
            status = self.pss_msg[index + 2]
            health = int(float(self.pss_msg[index + 3]))
            enemy.status = status
            enemy.center_x, enemy.center_y = cords
            enemy.health = health
            if index + 4 > len(self.pss_msg) - 1: return
            index += 4

    def send_stuff(self):
        # PSS
        game.sendto(
            f'{NAME},PSS,{self.player.center_x},{self.player.center_y},{self.player.status},{self.player.health}'.encode(),
            Server_ADDR)

    def on_update(self, delta_time):
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
        self.send_stuff()
        while True:
            data, addr = game.recvfrom(1024)
            if data.decode():
                name = data.decode().split(',')[0]
                type = data.decode().split(',')[1]

                if type == 'PSS':
                    self.pss_msg = data.decode().split(',')
                    break

                elif type == 'TDROP':
                    self.drops_number += 1
                    drop_name, drop_status = data.decode().split(',')[2], data.decode().split(',')[5]
                    drop_pos = (int(float(data.decode().split(',')[3][1:])),
                                int(float(data.decode().split(',')[4][1:data.decode().split(',')[4].find(')')])))
                    drop = Drop(drop_name, drop_pos, drop_status, self.drops_number)
                    self.drops_list.append(drop)
                    self.scene.add_sprite(LAYER_NAME_DROP, drop)
                    break

                elif type == 'PDROP':
                    drop_name = data.decode().split(',')[2]
                    drop_pos = (int(float(data.decode().split(',')[3][1:])),
                                int(float(data.decode().split(',')[4][1:data.decode().split(',')[4].find(')')])))
                    for drop in self.drops_list:
                        if drop.name != drop_name: continue
                        if drop.pos == drop_pos:
                            drop.kill()
                            self.drops_number -= 1
                            self.drops_list.remove(drop)
                    break

                else:
                    break


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, NAME)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
