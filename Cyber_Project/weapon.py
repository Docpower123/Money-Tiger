import arcade
import time
from settings import *


class Weapon(arcade.Sprite):
    def __init__(self, p_pos, name, p_status):
        super().__init__()
        self.direction = p_status.split('_')[0]
        self.p_pos = p_pos
        self.time = time.time()  # the time when you attacked with it
        self.name = name

        # graphic
        self.filename = f'./graphic/weapons/{name}/{self.direction}.png'
        self.texture = arcade.load_texture(self.filename)

        # on screen
        if self.direction == 'up':
            x_more, y_more = (-12, PLAYER_IMAGE_SIZE-16)
        elif self.direction == 'down':
            x_more, y_more = (-20, -PLAYER_IMAGE_SIZE+16)
        elif self.direction == 'right':
            x_more, y_more = (PLAYER_IMAGE_SIZE-16, -18)
        else:
            x_more, y_more = (-PLAYER_IMAGE_SIZE+16, -16)

        self.center_x = p_pos[0] + x_more
        self.center_y = p_pos[1] + y_more
