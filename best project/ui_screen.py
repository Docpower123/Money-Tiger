import arcade
from settings import *


class UI_SCREEN:
    def __init__(self, player):
        self.attribute_name = list(player.items.keys())
        self.attribute_num = len(self.attribute_name)
        self.attribute_info = list(player.items.values())
        self.attribute_index = 0
        self.ui_cords = []

        self.player = player

    def display(self, selection):
        # Drawing title "inventory!"
        title_x = self.player.center_x
        title_y = self.player.center_y + SCREEN_HEIGHT // 2 - 40
        arcade.draw_rectangle_filled(title_x, title_y, 300, 50, (74, 72, 72), 0)
        arcade.draw_text("Inventory :3", title_x - 80, title_y - 10, arcade.color.BLACK, 22)

        # Items update
        self.attribute_name = list(self.player.items.keys())
        self.attribute_num = len(self.attribute_name)
        self.attribute_info = list(self.player.items.values())
        self.attribute_index = 0

        # blocks cords setup
        # inventory
        for i in range(1, UI_SIZE // ROW_SIZE + 1):
            increment = SCREEN_WIDTH // ROW_SIZE
            for j in range(0, ROW_SIZE):
                if i == 2 and j == 2:  # Bar's idea and credit, all hail the mf Bar Abu Mazen
                    continue
                self.ui_cords.append((self.player.center_x + (j * increment) + (increment - SCREEN_WIDTH) // 2,
                                      self.player.center_y + SCREEN_HEIGHT / 2 - 160 * i))

        # Drawing inventory
        for (ui_screen_x, ui_screen_y) in self.ui_cords:
            # Drawing blocks
            arcade.draw_rectangle_filled(ui_screen_x, ui_screen_y, 120, 140, (74, 72, 72), 0)

            # Drawing items
            if self.attribute_index < self.attribute_num:
                name = self.attribute_name[self.attribute_index]
                amount = self.attribute_info[self.attribute_index]['amount']
                item_texture = arcade.load_texture(self.attribute_info[self.attribute_index]['graphic'])
                arcade.draw_text(name, ui_screen_x - 50, ui_screen_y + 50, arcade.color.BLACK, 15)
                arcade.draw_text(amount, ui_screen_x - 50, ui_screen_y - 60, arcade.color.BLACK, 15)
                arcade.draw_scaled_texture_rectangle(ui_screen_x, ui_screen_y, item_texture, 0.8)
                if name == selection:
                    arcade.draw_rectangle_outline(ui_screen_x, ui_screen_y, 120, 140, arcade.color.WHITE, 2)

            self.attribute_index += 1

        self.ui_cords = []
