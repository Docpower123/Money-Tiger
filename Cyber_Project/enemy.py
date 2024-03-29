import arcade
import time
import math
from settings import *


class Enemy(arcade.Sprite):
    def __init__(self, filename, scale, name, player, players, index):
        super().__init__(filename, scale)
        self.filename = filename
        self.scale = scale
        self.name = name
        self.player = player
        self.players = players
        self.attacked = self.player
        self.index = index
        self.layer = 'enemy'+str(index)

        # stats
        self.health = enemy_data[name]['health']

        # movement
        self.auto_movement_time = time.time()
        self.auto_movement_time2 = time.time()
        self.movement_options = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        # animation
        self.texture = arcade.load_texture(filename)
        self.animation_time = time.time()
        self.status = 'idle'
        self.cur_texture_index = 0
        if name == 'Raccoon':
            self.animations = raccoon_animations
        elif name == 'Squid':
            self.animations = squid_animations
        else:
            self.animations = spirit_bamboo_animations

    def animation(self):
        time_passed = time.time() - self.animation_time
        if time_passed < 0.1:
            return
        self.animation_time = time.time()

        path = ENEMY_PATH + self.name + '/' + self.status + '/'
        self.cur_texture_index += 1
        if self.status == 'idle':
            if self.cur_texture_index > len(self.animations['idle'])-1:
                self.cur_texture_index = 0
            self.texture = arcade.load_texture(path + self.animations['idle'][self.cur_texture_index])

        if self.status == 'attack':
            if self.cur_texture_index > len(self.animations['attack'])-1:
                self.cur_texture_index = 0
            self.texture = arcade.load_texture(path + self.animations['attack'][self.cur_texture_index])

        else:
            if self.cur_texture_index > len(self.animations['move'])-1:
                self.cur_texture_index = 0
            self.texture = arcade.load_texture(path + self.animations['move'][self.cur_texture_index])

    def check_who_to_attack(self):
        min_distance_vec = (self.player.center_x - self.center_x, self.player.center_y - self.center_y)
        min_distance = math.sqrt((min_distance_vec[0])**2 + (min_distance_vec[1])**2)

        for player in self.players:
            distance_vec = (player.center_x - self.center_x, player.center_y - self.center_y)
            distance = math.sqrt((distance_vec[0])**2 + (distance_vec[1])**2)
            if min_distance > distance:
                min_distance = distance
                self.attacked = player
            else:
                self.attacked = self.player

    def e_update(self):
        self.animation()
        self.check_who_to_attack()
