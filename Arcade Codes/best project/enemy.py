import arcade
import time
from settings import *


class Enemy(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.filename = filename
        self.scale = scale

        # animation
        self.texture = arcade.load_texture(filename)
        self.animation_time = time.time()
        self.status = 'down'
        self.cur_texture_index = 0

    def animation(self):
        time_passed = time.time() - self.animation_time
        if time_passed < 0.1:
            return
        self.animation_time = time.time()
        path = ENEMY_PATH + self.status + '/'
        self.cur_texture_index += 1
        if self.cur_texture_index > 3:
            self.cur_texture_index = 0
        if 'idle' in self.status:
            self.texture = arcade.load_texture(path + animations[self.status][0])
        else:
            self.texture = arcade.load_texture(path + animations[self.status][self.cur_texture_index])
