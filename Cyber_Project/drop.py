import arcade
from settings import *


DIRECTION_MAP = {
    'up':    (0, THROW_DISTANCE),
    'down':  (0, -THROW_DISTANCE),
    'right': (THROW_DISTANCE, 0),
    'left':  (-THROW_DISTANCE, 0),
}


class Drop(arcade.Sprite):
    def __init__(self, name, pos, status, index):
        super().__init__()
        direction = status.split('_')[0]
        self.name = name
        self.pos = pos
        self.layer = f'drop{index}'
        if 'potion' in name:
            self.scale = 0.4

        # graphic
        self.filename = f'./graphic/drops/{name}.png'
        self.texture = arcade.load_texture(self.filename)

        # on screen
        x_more, y_more = DIRECTION_MAP.get(direction, (0, 0))
        self.center_x = int(float(pos[0])) + x_more
        self.center_y = int(float(pos[1])) + y_more
