import arcade
from settings import *


class Drop(arcade.Sprite):
    def __init__(self, name, pos, status, index):
        super().__init__()
        direction = status.split('_')[0]
        self.name = name
        self.layer = 'drop'+str(index)
        if 'potion' in name:
            self.scale = 0.4


        # graphic
        self.filename = f'./graphic/drops/{name}.png'
        self.texture = arcade.load_texture(self.filename)

        # on screen
        if direction == 'up':
            x_more, y_more = (0, THROW_DISTANCE)
        elif direction == 'down':
            x_more, y_more = (0, -THROW_DISTANCE)
        elif direction == 'right':
            x_more, y_more = (THROW_DISTANCE, 0)
        elif direction == 'left':
            x_more, y_more = (-THROW_DISTANCE, 0)
        else:
            x_more, y_more = (0, 0)

        self.center_x = pos[0] + x_more
        self.center_y = pos[1] + y_more
