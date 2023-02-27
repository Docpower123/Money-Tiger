import arcade
from settings import *


class Weapon(arcade.Sprite):
    def __init__(self, player):
        super().__init__()
        self.direction = player.status.split('_')[0]
        self.player = player

        # graphic
        self.filename = f'./graphic/weapons/{player.weapon}/{self.direction}.png'
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

        self.center_x = self.player.center_x + x_more
        self.center_y = self.player.center_y + y_more
