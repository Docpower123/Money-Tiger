import arcade
import time
from settings import *


class Player(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.filename = filename
        self.scale = scale
        self.layer = 'player'

        # Animate
        self.texture = arcade.load_texture(filename)
        self.cur_texture_index = 0
        self.status = 'down'
        self.animation_time = time.time()

        # Stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 3}
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
        self.drop = DEFAULT_DROP
        self.current_drop = None

        # damage player
        self.vulnerable = True
        self.hurt_time = time.time()

        # Attack!
        self.weapon = DEFAULT_WEAPON
        self.current_attack = None
        self.attacking = False
        self.attack_time = time.time()

        # Magic
        self.magic = DEFAULT_MAGIC
        self.current_magic = None
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
        if self.change_x > 0:
            self.status = 'right'
        elif self.change_x < 0:
            self.status = 'left'
        elif self.change_y > 0:
            self.status = 'up'
        elif self.change_y < 0:
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

    def player_move(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0

        if self.bottom < 0:
            self.bottom = 0

    def update(self):
        self.get_status()
        self.animation()
        self.energy_recovery()
        if not self.attacking and not self.magicing:
            self.player_move()
