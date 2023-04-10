import arcade
import time


class Magic(arcade.Sprite):
    def __init__(self, p_pos, name, p_status):
        self.p_pos = p_pos
        self.center_x, self.center_y = p_pos
        self.name = name
        self.time = time.time()

        direction = p_status.split('_')[0]
        self.direction = {
            'up': (0, 1),
            'down': (0, -1),
            'right': (1, 0),
            'left': (-1, 0),
        }[direction]

        file_name = f'./graphic/magic/{name}/full.png'
        self.texture = arcade.load_texture(file_name)
