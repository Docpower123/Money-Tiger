import arcade
from settings import *


class Magic(arcade.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        direction = player.status.split('_')[0]

        if direction == 'up':
            self.direction = (0, 1)
        elif direction == 'down':
            self.direction = (0, -1)
        elif direction == 'right':
            self.direction = (1, 0)
        else:
            self.direction = (-1, 0)

    def magic_update(self, ui_screen):
        file_name = f'./graphic/magic/{self.player.magic}/full.png'
        self.texture = arcade.load_texture(file_name)

        potions_conditions = (self.player.magic == 'potion' or self.player.magic == 'potion1' and
                            magic_data['potion']['cost'] <= self.player.energy)

        flame_conditions = (self.player.magic == 'flame' and
                            magic_data['flame']['cost'] <= self.player.energy)

        heal_conditions = (self.player.magic == 'heal' and
                           magic_data['heal']['cost'] <= self.player.energy and
                           self.player.health < self.player.stats['health'])

        # potion
        if potions_conditions:
            self.scale = 0.2
            self.player.energy -= magic_data[self.player.magic]['cost']
            self.center_x = self.player.center_x + self.direction[0]*32
            self.center_y = self.player.center_y + self.direction[1]*32
            # reducing amount of heal
            self.player.items[self.player.magic]['amount'] -= 1
            # amount is 0, this magic is no more
            if self.player.items[self.player.magic]['amount'] == 0:
                self.player.items.pop(self.player.magic, None)
                self.player.magic = DEFAULT_MAGIC
                ui_screen.attribute_index -= 1

        # flame
        elif flame_conditions:
            self.player.energy -= magic_data['flame']['cost']
            self.center_x = self.player.center_x + self.direction[0]*12*20
            self.center_y = self.player.center_y + self.direction[1]*12*20

        # heal
        elif heal_conditions:
            # decrease energy, increase health
            self.player.energy -= magic_data['heal']['cost']
            if self.player.stats['health'] - self.player.health < magic_data['heal']['strength']:
                self.player.health = self.player.stats['health']
            else:
                self.player.health += magic_data['heal']['strength']
            # cords
            self.center_x = self.player.center_x
            self.center_y = self.player.center_y
            # reducing amount of heal
            self.player.items['heal']['amount'] -= 1
            # amount is 0, this magic is no more
            if self.player.items[self.player.magic]['amount'] == 0:
                self.player.items.pop(self.player.magic, None)
                self.player.magic = DEFAULT_MAGIC
                ui_screen.attribute_index -= 1
