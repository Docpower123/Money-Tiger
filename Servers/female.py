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
NAME = 'FEMALE'
ADDR = (FEMALE_IP, FEMALE_PORT)
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

        # Players
        self.player = Player(PLAYER_IMAGE, SPRITE_SCALING)
        self.player1 = Player(PLAYER_IMAGE, SPRITE_SCALING)
        self.players = {'FEMALE': self.player, 'MALE': self.player1}
        self.player_list = arcade.SpriteList()
        self.physics_engine = None

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

        # Draw all the sprites.
        self.scene.draw()

        # Physics :(
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, walls=self.scene['Players'])

    def on_draw(self):
        # This command has to happen before we start drawing
        self.clear()
        self.camera.use()

        # Draw all the sprites.
        self.scene.draw()

        # Inventory
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
        if self.player.attacking or self.player.magicing:
            return
        # attack!
        if key == arcade.key.SPACE:
            self.create_attack()
        # magic
        elif key == arcade.key.M:
            self.create_magic()
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
        # regular movement
        if key == arcade.key.W:
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

    # ------------------ enemies ------------------

    def draw_enemies(self):
        for monster_data in enemy_data.values():
            for monster in self.tile_map.sprite_lists[monster_data['layer']]:
                enemy = Enemy(monster_data['filename'], ENTITY_SIZE, monster_data['layer'], self.player,
                              self.enemies_number)
                enemy.center_x, enemy.center_y = monster.center_x, monster.center_y

                self.enemies_number += 1
                self.enemies_list.append(enemy)
                #try:
                    #enemies_collision = self.scene[LAYER_NAME_BARRIER].append(self.player)
                #except:
                    #enemies_collision = self.scene[LAYER_NAME_BARRIER]
                #physics = arcade.PhysicsEngineSimple(enemy, walls=enemies_collision)
                #self.enemies_physics.append(physics)

                self.scene.add_sprite(LAYER_NAME_ENEMY, enemy)

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
        self.drops_list.append(drop1)
        self.scene.add_sprite(LAYER_NAME_DROP, drop1)

        # drop 2
        self.drops_number += 1
        drop_name = choice(enemy_data[monster.name]['drop'])
        drop_pos = (monster.center_x, monster.center_y)
        drop2 = Drop(drop_name, drop_pos, monster.status, self.drops_number)
        self.drops_list.append(drop2)
        self.scene.add_sprite(LAYER_NAME_DROP, drop2)

    def enemies_update(self):
        # movement & health & death
        if self.enemies_list:
            for monster in self.enemies_list:
                # update
                monster.e_update()
                if monster.status == 'idle':
                    self.enemies_auto_move(monster)
                # death!
                if monster.health <= 0:
                    # drop
                    self.enemy_create_drop(monster)
                    # dead
                    monster.kill()
                    self.enemies_number -= 1
                    self.enemies_list.remove(monster)
                    self.dead_enemies_list.append(monster)

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
        for monster in self.enemies_list:
            if arcade.check_for_collision(self.player.current_attack, monster):
                monster.health -= self.player.stats['attack']

                if self.player.current_attack.direction == 'up':
                    direction = (0, 1)
                elif self.player.current_attack.direction == 'down':
                    direction = (0, -1)
                elif self.player.current_attack.direction == 'right':
                    direction = (1, 0)
                else:
                    direction = (-1, 0)
                monster.center_x += direction[0] * 64
                monster.center_y += direction[1] * 64

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
                if monster.status != 'attack':
                    continue
                # non-spirit monsters attack from close
                elif monster.name != 'Spirit' and arcade.check_for_collision(self.player, monster):
                    if self.player.health - enemy_data[monster.name]['damage'] <= 0:
                        self.player.health = 0
                    elif self.player.health > 0:
                        self.player.health -= enemy_data[monster.name]['damage']
                    else:
                        self.player.health = 0

                # Spirit attack from far
                elif monster.name == 'Spirit':
                    if self.player.health - enemy_data[monster.name]['damage'] <= 0:
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
        # 	this drop is no more on the floor :(
        drop.kill()
        self.drops_number -= 1
        self.drops_list.remove(drop)

    def check_if_pick_up_drops(self):
        for drop in self.drops_list:
            if arcade.check_for_collision(self.player, drop):
                self.pick_up_drops(drop)

    # ------------------ update ------------------

    def on_update(self, delta_time):
        # Screen
        self.center_camera_to_player()

        # Players
        self.player_list.update()
        self.player.update()
        while True:
            game.sendto(f'{NAME}, {self.player.center_x}, {self.player.center_y}'.encode(), Server_ADDR)
            data, addr = game.recvfrom(1024)
            if data.decode():
                try:
                    cords = data.decode().split(',')[1], data.decode().split(',')[2]
                    name = data.decode().split(',')[0]
                    if name == 'MALE' and (self.player1.center_x != int(cords[0]) or self.player1.center_y != int(
                            cords[1])):
                        print("recieve")
                        self.player1.center_x = int(cords[0])
                        self.player1.center_y = int(cords[1])
                finally:
                    break


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, 'FEMALE')
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
