import arcade
import time
import math
from settings import *


class Enemy(arcade.Sprite):
    def __init__(self, filename, scale, name, player, index):
        super().__init__(filename, scale)
        self.filename = filename
        self.scale = scale
        self.name = name
        self.player = player
        self.layer = 'enemy'+str(index)

        # stats
        self.health = enemy_data[name]['health']

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

    def get_player_distance_direction(self):
        distance_vec = (self.player.center_x - self.center_x, self.player.center_y - self.center_y)
        distance = math.sqrt((distance_vec[0])**2 + (distance_vec[1])**2)

        if distance > 0:
            if distance_vec[0] < 0 and distance_vec[1] < 0:
                direction = (-1, -1)
            elif distance_vec[0] > 0 and distance_vec[1] > 0:
                direction = (1, 1)
            elif distance_vec[0] < 0 < distance_vec[1]:
                direction = (-1, 1)
            else:
                direction = (1, -1)
        else:
            direction = (0, 0)

        return distance, direction

    def get_status(self):
        distance = self.get_player_distance_direction()[0]
        notice_radius = enemy_data[self.name]['notice_radius']
        attack_radius = enemy_data[self.name]['attack_radius']
        if distance <= attack_radius:
            self.status = 'attack'
        elif distance <= notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def e_move(self):
        self.change_x = self.get_player_distance_direction()[1][0]
        self.change_y = self.get_player_distance_direction()[1][1]

        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0

        if self.bottom < 0:
            self.bottom = 0

    def e_update(self):
        self.animation()
        self.get_status()
        if self.status == 'move':
            self.e_move()
