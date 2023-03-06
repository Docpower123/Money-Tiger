import arcade
import time


class Magic(arcade.Sprite):
    def __init__(self, p_pos, name, p_status):
        super().__init__()
        self.p_pos = p_pos
        self.center_x, self.center_y = p_pos
        self.name = name
        self.time = time.time()
        direction = p_status.split('_')[0]

        if direction == 'up':
            self.direction = (0, 1)
        elif direction == 'down':
            self.direction = (0, -1)
        elif direction == 'right':
            self.direction = (1, 0)
        else:
            self.direction = (-1, 0)

        file_name = f'./graphic/magic/{name}/full.png'
        self.texture = arcade.load_texture(file_name)
