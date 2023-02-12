import arcade
from settings import *


class UI:
    def __init__(self, player):
        self.player = player
        self.x = 0
        self.y = 0

    def draw_weapon_block(self):
        arcade.draw_rectangle_filled(self.x, self.y, 64, 64, (74, 72, 72), 0)
        arcade.draw_rectangle_outline(self.x, self.y, 64, 64, arcade.color.BLACK, 2)

        if self.player.weapon is not None:
            file_name = self.player.items[self.player.weapon]['graphic']
            weapon_texture = arcade.load_texture(file_name)
            arcade.draw_scaled_texture_rectangle(self.x, self.y, weapon_texture, 0.8)

            amount = self.player.items[self.player.weapon]['amount']
            if amount != 'permanent':
                arcade.draw_text(amount, self.x, self.y, arcade.color.WHITE)

    def draw_magic_block(self):
        arcade.draw_rectangle_filled(self.x + 64, self.y, 64, 64, (74, 72, 72), 0)
        arcade.draw_rectangle_outline(self.x + 64, self.y, 64, 64, arcade.color.BLACK, 2)

        if self.player.magic is not None:
            file_name = self.player.items[self.player.magic]['graphic']
            magic_texture = arcade.load_texture(file_name)
            if 'potion' in self.player.magic:
                size = 0.4
            else:
                size = 1.2
            arcade.draw_scaled_texture_rectangle(self.x + 64, self.y, magic_texture, size)

            amount = self.player.items[self.player.magic]['amount']
            if amount != 'permanent':
                arcade.draw_text(amount, self.x + 64 + 18, self.y - 25, arcade.color.WHITE, 16)

    def draw_drop_block(self):
        arcade.draw_rectangle_filled(self.x + 128, self.y, 64, 64, (74, 72, 72), 0)
        arcade.draw_rectangle_outline(self.x + 128, self.y, 64, 64, arcade.color.BLACK, 2)

        if self.player.item is not None:
            file_name = self.player.items[self.player.item]['graphic']
            drop_texture = arcade.load_texture(file_name)
            arcade.draw_scaled_texture_rectangle(self.x + 128, self.y, drop_texture, 1.2)

            amount = self.player.items[self.player.item]['amount']
            if amount != 'permanent':
                arcade.draw_text(amount, self.x + 128 + 18, self.y - 25, arcade.color.WHITE, 16)

    def draw_health(self):
        arcade.draw_rectangle_filled(self.x + 80, self.y + SCREEN_HEIGHT - 105, 64, 84, (74, 72, 72), 0)
        arcade.draw_rectangle_outline(self.x + 80, self.y + SCREEN_HEIGHT - 105, 64, 84, arcade.color.BLACK, 2)

        if self.player.health is not None:
            health = self.player.health
            max_health = self.player.stats['health']
            if max_health * 0.8 < health <= max_health:
                file_name = './graphic/health/full_h.png'
            elif max_health * 0.5 < health <= max_health * 0.8:
                file_name = './graphic/health/most_h.png'
            elif max_health * 0.3 < health <= max_health * 0.5:
                file_name = './graphic/health/half_h.png'
            elif 0 < health <= max_health*0.3:
                file_name = './graphic/health/dying_h.png'
            else:
                file_name = './graphic/health/zero_h.png'

            health_texture = arcade.load_texture(file_name)
            arcade.draw_scaled_texture_rectangle(self.x + 80, self.y + SCREEN_HEIGHT - 90, health_texture, 0.15)
            arcade.draw_text(int(health), self.x + 60, self.y + SCREEN_HEIGHT - 140, arcade.color.WHITE, 15)

    def draw_energy(self):
        arcade.draw_rectangle_filled(self.x, self.y + SCREEN_HEIGHT - 105, 64, 84, (74, 72, 72), 0)
        arcade.draw_rectangle_outline(self.x, self.y + SCREEN_HEIGHT - 105, 64, 84, arcade.color.BLACK, 2)

        if self.player.energy is not None:
            energy = self.player.energy
            max_energy = self.player.stats['energy']
            if max_energy*0.8 < energy <= max_energy:
                file_name = './graphic/energy/full_e.png'
            elif max_energy*0.5 < energy <= max_energy*0.8:
                file_name = './graphic/energy/most_e.png'
            elif max_energy*0.3 < energy <= max_energy*0.5:
                file_name = './graphic/energy/half_e.png'
            elif 0 < energy <= max_energy*0.3:
                file_name = './graphic/energy/dying_e.png'
            else:
                file_name = './graphic/energy/zero_e.png'

            energy_texture = arcade.load_texture(file_name)
            arcade.draw_scaled_texture_rectangle(self.x, self.y + SCREEN_HEIGHT - 90, energy_texture, 0.2)
            arcade.draw_text(int(energy), self.x - 20, self.y + SCREEN_HEIGHT - 140, arcade.color.WHITE, 15)

    def ui_update(self):
        self.x = self.player.center_x - SCREEN_WIDTH / 2 + 50
        self.y = self.player.center_y - SCREEN_HEIGHT / 2 + 50

    def display(self):
        self.ui_update()
        self.draw_drop_block()
        self.draw_magic_block()
        self.draw_weapon_block()
        self.draw_energy()
        self.draw_health()
