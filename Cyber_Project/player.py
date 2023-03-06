import arcade
import time
from settings import *


class Player(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.filename = filename
        self.scale = scale
        self.layer = 'player'

        # Movement
        self.auto_movement = False
        self.auto_movement_time = time.time()
        self.auto_movement_time2 = time.time()
        self.movement_options = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        # Animate
        self.texture = arcade.load_texture(filename)
        self.cur_texture_index = 0
        self.status = 'down_idle'
        self.animation_time = time.time()

        # Stats
        self.stats = PLAYER_STATS
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.speed = self.stats['speed']
        self.items = {
            'sword': {'amount': 'permanent', 'type': 'weapon', 'graphic': './graphic/weapons/sword/full.png'},
            'lance': {'amount': 'permanent', 'type': 'weapon', 'graphic': './graphic/weapons/lance/full.png'},
            'axe': {'amount': 'permanent', 'type': 'weapon', 'graphic': './graphic/weapons/axe/full.png'},
            'rapier': {'amount': 'permanent', 'type': 'weapon', 'graphic': './graphic/weapons/rapier/full.png'},
            'sai': {'amount': 'permanent', 'type': 'weapon', 'graphic': './graphic/weapons/sai/full.png'},
            'flame': {'amount': 'permanent', 'type': 'magic', 'graphic': './graphic/magic/flame/fire.png'},
            'eraser': {'amount': 4, 'type': 'drop', 'graphic': './graphic/drops/eraser.png'},
            'heal': {'amount': 4, 'type': 'magic', 'graphic': './graphic/magic/heal/heal.png'}}
        self.selection_index = 0

        # drop
        self.item = DEFAULT_ITEM
        self.last_drop = None

        # damage player
        self.vulnerable = True
        self.hurt_time = time.time()

        # Attack!
        self.weapon = DEFAULT_WEAPON
        self.current_attack = arcade.Sprite()
        self.attacking = False
        self.attack_time = time.time()

        # Magic
        self.magic = DEFAULT_MAGIC
        self.current_magic = arcade.Sprite()
        self.magicing = False
        self.magic_time = time.time()

    def animation(self):
        time_passed = time.time() - self.animation_time
        if time_passed < 0.1:
            return
        self.animation_time = time.time()
        path = PLAYER_PATH + self.status + '/'
        self.cur_texture_index += 1
        if self.cur_texture_index > 3:
            self.cur_texture_index = 0
        if 'idle' in self.status or 'attack' in self.status:
            self.texture = arcade.load_texture(path + player_animations[self.status][0])
        else:
            self.texture = arcade.load_texture(path + player_animations[self.status][self.cur_texture_index])

    def get_status(self):
        if self.change_x > 0 and self.status != 'right':
            self.status = 'right'
        elif self.change_x < 0 and self.status != 'left':
            self.status = 'left'
        elif self.change_y > 0 and self.status != 'up':
            self.status = 'up'
        elif self.change_y < 0 and self.status != 'down':
            self.status = 'down'
        elif 'idle' not in self.status and 'attack' not in self.status:
            self.status = self.status + '_idle'
        elif self.attacking or self.magicing:
            self.change_x = 0
            self.change_y = 0
            if 'attack' not in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def energy_recovery(self):
        if self.energy < self.stats['energy']:
            self.energy += 0.01 * self.stats['magic']
        else:
            self.energy = self.stats['energy']

    def magic_update(self, ui_screen, magic):
        potions_conditions = (self.magic == 'potion' or self.magic == 'potion1' and
                              magic_data['potion']['cost'] <= self.magic)

        flame_conditions = (self.magic == 'flame' and
                            magic_data['flame']['cost'] <= self.energy)

        heal_conditions = (self.magic == 'heal' and
                           magic_data['heal']['cost'] <= self.energy and
                           self.health < self.stats['health'])

        # potion
        if potions_conditions:
            magic.scale = 0.2
            self.energy -= magic_data[self.magic]['cost']
            magic.center_x = self.center_x + magic.direction[0]*32
            magic.center_y = self.center_y + magic.direction[1]*32
            # reducing amount of heal
            self.items[self.magic]['amount'] -= 1
            # amount is 0, this magic is no more
            if self.items[self.magic]['amount'] == 0:
                self.items.pop(self.magic, None)
                self.magic = DEFAULT_MAGIC
                ui_screen.attribute_index -= 1
            return True

        # flame
        elif flame_conditions:
            self.energy -= magic_data['flame']['cost']
            magic.center_x = self.center_x + magic.direction[0]*12*20
            magic.center_y = self.center_y + magic.direction[1]*12*20
            return True

        # heal
        elif heal_conditions:
            # decrease energy, increase health
            self.energy -= magic_data['heal']['cost']
            if self.stats['health'] - self.health < magic_data['heal']['strength']:
                self.health = self.stats['health']
            else:
                self.health += magic_data['heal']['strength']
            # cords
            magic.center_x = self.center_x
            magic.center_y = self.center_y
            # reducing amount of heal
            self.items['heal']['amount'] -= 1
            # amount is 0, this magic is no more
            if self.items[self.magic]['amount'] == 0:
                self.items.pop(self.magic, None)
                self.magic = DEFAULT_MAGIC
                ui_screen.attribute_index -= 1
            return True

        # don't have the necessary stuff for doing magic
        else:
            return False

    def player_move(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

    def update(self):
        self.animation()
        self.energy_recovery()
        if not self.attacking and not self.magicing:
            self.player_move()
