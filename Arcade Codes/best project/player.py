import arcade
import time
from settings import *


class Player(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.filename = filename
        self.scale = scale
        self.speed = PLAYER_SPEED

        # Animate
        self.texture = arcade.load_texture(filename)
        self.cur_texture_index = 0
        self.status = 'down'
        self.animation_time = time.time()

    def animation(self):
        time_passed = time.time() - self.animation_time
        if time_passed < 0.1:
            return
        self.animation_time = time.time()
        path = PLAYER_PATH + self.status+'/'
        self.cur_texture_index += 1
        if self.cur_texture_index > 3:
            self.cur_texture_index = 0
        if 'idle' in self.status:
            self.texture = arcade.load_texture(path+animations[self.status][0])
        else:
            self.texture = arcade.load_texture(path+animations[self.status][self.cur_texture_index])

    def get_status(self):
        if self.change_x > 0:
            self.status = 'right'
        elif self.change_x < 0:
            self.status = 'left'
        elif self.change_y > 0:
            self.status = 'up'
        elif self.change_y < 0:
            self.status = 'down'
        elif 'idle' not in self.status:
            self.status += '_idle'

    def update(self):
        # Move player.
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0

        if self.bottom < 0:
            self.bottom = 0
