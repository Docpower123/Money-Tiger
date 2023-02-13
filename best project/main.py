import arcade
import time
from random import choice

import settings
from settings import *
from player import Player
from enemy import Enemy
from weapon import Weapon
from magic import Magic
from drop import Drop
from ui_screen import UI_SCREEN
from ui import UI


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(SCEEN_COLOR)

        # setup
        self.scene = arcade.Scene()
        self.physics_engine = None
        self.camera = arcade.Camera(self.width, self.height)
        self.tile_map = arcade.load_tilemap(settings.TILE_MAP, settings.TILE_SIZE, settings.LAYER_OPTIONS)
        self.physics_engine = None

        # player
        self.player = Player(PLAYER_IMAGE, ENTITY_SIZE)
        self.drops_list = []
        self.drops_number = 0

        # Inventory
        self.ui_screen = UI_SCREEN(self.player)
        self.ui = UI(self.player)
        self.game_paused_ui = False
        self.selection = 'sword'

        # enemies
        self.enemies_list = []
        self.enemies_physics = []
        self.enemies_number = 0
# ------------------ set up ------------------

    def setup(self):
        # Set up the seen screen
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Set up the player
        player_x = self.tile_map.sprite_lists[LAYER_NAME_PLAYER][0].center_x
        player_y = self.tile_map.sprite_lists[LAYER_NAME_PLAYER][0].center_y
        self.player.center_x, self.player.center_y = (player_x, player_y)
        self.scene.add_sprite(self.player.layer, self.player)

        # enemies
        self.draw_enemies()

        # Physics :(
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, walls=self.scene[LAYER_NAME_BARRIER])

    def on_draw(self):
        # Clear the screen to the background color
        self.clear()

        # Draw our seen screen
        self.scene.draw()
        self.camera.use()

        # enemies health
        for monster in self.enemies_list:
            if monster.name != 'Raccoon':
                arcade.draw_text(monster.health, monster.center_x, monster.center_y+34, arcade.color.WHITE, 14)
            else:
                arcade.draw_text(monster.health, monster.center_x, monster.center_y+104, arcade.color.WHITE, 14)

        # inventory
        self.ui.display()
        if self.game_paused_ui:
            self.ui_screen.display(self.selection)

    def main_cooldowns(self):
        current_time = time.time()

        if self.player.attacking:
            if current_time - self.player.attack_time >= weapon_data[self.player.weapon]['cooldown']:
                self.player.attacking = False
                self.destroy_attack()

        if not self.player.vulnerable:
            if current_time - self.player.hurt_time >= 0.4:
                self.player.vulnerable = True

    def center_camera_to_player(self):
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

        # physics
        for physics in self.enemies_physics:
            physics.update()

# ------------------ key input ------------------

    def on_key_press(self, key, modifiers):
        if self.player.attacking or self.player.magicing:
            return
        if key == arcade.key.SPACE:
            self.create_attack()
        elif key == arcade.key.M:
            self.create_magic()
        elif key == arcade.key.W:
            self.player.change_y = self.player.speed
        elif key == arcade.key.S:
            self.player.change_y = -self.player.speed
        elif key == arcade.key.A:
            self.player.change_x = -self.player.speed
        elif key == arcade.key.D:
            self.player.change_x = self.player.speed

    def on_key_release(self, key, modifiers):
        # regular movement
        if key == arcade.key.W:
            self.player.change_y = 0
        elif key == arcade.key.S:
            self.player.change_y = 0
        elif key == arcade.key.A:
            self.player.change_x = 0
        elif key == arcade.key.D:
            self.player.change_x = 0

        # magic! 0-0
        elif key == arcade.key.M and self.player.current_magic and self.player.magicing:
            self.destroy_magic()

        # drops :P
        elif key == arcade.key.Q and self.player.drop is not None:
            self.create_drop()

        # inventory!
        elif key == arcade.key.E:
            self.game_paused_ui = not self.game_paused_ui

        elif self.game_paused_ui:
            if key == arcade.key.RIGHT:
                self.player.selection_index += 1
                if self.player.selection_index > len(list(self.player.items.keys())) - 1:
                    self.player.selection_index = 0
                self.selection = list(self.player.items.keys())[self.player.selection_index]

            elif key == arcade.key.LEFT:
                self.player.selection_index -= 1
                if self.player.selection_index < 0:
                    self.player.selection_index = len(list(self.player.items.keys())) - 1
                self.selection = list(self.player.items.keys())[self.player.selection_index]

            elif key == arcade.key.UP:
                # weapon
                if list(self.player.items.values())[self.player.selection_index]['type'] == 'weapon':
                    self.player.weapon = list(self.player.items.keys())[self.player.selection_index]
                    self.player.current_attack = Weapon(self.player)

                # magic
                elif list(self.player.items.values())[self.player.selection_index]['type'] == 'magic':
                    self.player.magic = list(self.player.items.keys())[self.player.selection_index]

                # drop
                elif list(self.player.items.values())[self.player.selection_index]['type'] == 'drop':
                    self.player.drop = list(self.player.items.keys())[self.player.selection_index]

# ------------------ enemies ------------------

    def draw_enemies(self):
        for monster_data in enemy_data.values():
            for monster in self.tile_map.sprite_lists[monster_data['layer']]:
                enemy = Enemy(monster_data['filename'], ENTITY_SIZE, monster_data['layer'], self.player,
                              self.enemies_number)
                enemy.center_x, enemy.center_y = monster.center_x, monster.center_y

                self.enemies_number += 1
                self.enemies_list.append(enemy)
                physics = arcade.PhysicsEngineSimple(enemy, walls=self.scene[LAYER_NAME_BARRIER])
                self.enemies_physics.append(physics)

                self.scene.add_sprite(enemy.layer, enemy)

    def enemy_create_drop(self, monster):
        # drops list
        self.drops_number += 1
        self.drops_list.append(self.player.current_drop)

        # making sprite
        drop_name = choice(enemy_data[monster.name]['drop'])
        drop_pos = (monster.center_x, monster.center_y)
        drop = Drop(drop_name, drop_pos, monster.status, self.drops_number)
        self.scene.add_sprite(drop.layer, drop)

    def enemies_update(self):
        # movement & health & death
        if self.enemies_list:
            for monster in self.enemies_list:
                # update
                monster.e_update()
                # death!
                if monster.health <= 0:
                    # drop
                    if choice([1, 2, 3, 4, 5]) != 3:
                        self.enemy_create_drop(monster)
                    # dead
                    self.scene.remove_sprite_list_by_name(monster.layer)
                    self.enemies_number -= 1
                    self.enemies_list.remove(monster)

# ------------------ attack! ------------------

    def create_attack(self):
        self.player.attack_time = time.time()
        self.player.current_attack = Weapon(self.player)
        self.scene.add_sprite(LAYER_NAME_WEAPON, self.player.current_attack)
        self.player.attacking = True

    def destroy_attack(self):
        self.player.attacking = False
        self.scene.remove_sprite_list_by_name(LAYER_NAME_WEAPON)

        for monster in self.enemies_list:
            if arcade.check_for_collision(self.player.current_attack, monster):
                monster.health -= self.player.stats['attack']

    def damage_player(self):
        if self.player.vulnerable:
            self.player.vulnerable = False
            self.player.hurt_time = time.time()
            for monster in self.enemies_list:
                if arcade.check_for_collision(self.player, monster):
                    if self.player.health > 0:
                        self.player.health -= enemy_data[monster.name]['damage']
                    else:
                        self.player.health = 0

# ------------------ magic ------------------
    def create_magic(self):
        self.player.magic_time = time.time()
        self.player.magicing = True
        self.player.current_magic = Magic(self.player)
        self.player.current_magic.magic_update(self.ui_screen)
        self.scene.add_sprite(LAYER_NAME_MAGIC, self.player.current_magic)

    def destroy_magic(self):
        self.player.magicing = False
        self.scene.remove_sprite_list_by_name(LAYER_NAME_MAGIC)

        if self.player.magic == 'flame':
            for monster in self.enemies_list:
                if arcade.check_for_collision(self.player.current_magic, monster):
                    monster.health -= self.player.stats['attack']

# ------------------ drop ------------------

    def create_drop(self):
        self.drops_number += 1
        self.player.current_drop = Drop(self.player, self.player.drop, self.drops_number)
        self.drops_list.append(self.player.current_drop)
        self.scene.add_sprite(self.player.current_drop.layer, self.player.current_drop)
        # reducing amount of drop
        self.player.items[self.player.drop]['amount'] -= 1
        # amount is 0, this drop is no more
        if self.player.items[self.player.drop]['amount'] == 0:
            self.player.items.pop(self.player.drop, None)
            self.player.drop = None
            self.ui_screen.attribute_index -= 1

    def pick_up_drops(self):
        for drop in self.drops_list:
            if arcade.check_for_collision(self.player, drop):
                if drop.name in self.player.items.keys():
                    #  increasing the amount of this drop - player pick up! :)
                    self.player.items[drop.name]['amount'] += 1
                else:
                    #  adding this drop to player's items list
                    self.player.items[drop.name] = {}
                    self.player.items[drop.name].update(drop_data[drop.name])
                    self.ui_screen.attribute_index += 1

                # 	this drop is no more on the floor :(
                self.scene.remove_sprite_list_by_name(drop.layer)
                self.drops_number -= 1
                self.drops_list.remove(drop)

# ------------------ update ------------------

    def on_update(self, delta_time):
        self.main_cooldowns()
        if not self.player.attacking and not self.player.magicing:
            self.physics_engine.update()
        self.enemies_update()
        self.damage_player()
        self.player.update()
        self.pick_up_drops()
        self.center_camera_to_player()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()


# ------------------ to fix ------------------
# ui runs away when player is in (0,0)
# drop stuck in barrier

# ------------------ to add ------------------
# respawning enemies
# enemies drop
# enemy attack from far
# much bigger map
# AI auto movement
# AI auto movement for enemies

# ------------------ noice ideas ------------------
# upgrade system (maybe with magic)
# shop
# exp - levels
# better graphics
# more items
