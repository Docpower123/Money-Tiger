import time

import arcade
from settings import *
from player import Player
from enemy import Enemy


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(SCEEN_COLOR)

        # setup
        self.scene = None
        self.physics_engine = None
        self.camera = None
        self.tile_map = None
        self.physics_engine = None

        # player
        self.player = Player(PLAYER_IMAGE, ENTITY_SIZE)

    def setup(self):
        # Set up the seen screen
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(self.width, self.height)
        self.tile_map = arcade.load_tilemap(TILE_MAP, TILE_SIZE, LAYER_OPTIONS)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Set up the player
        player_x = self.tile_map.sprite_lists[LAYER_NAME_PLAYER][0].center_x
        player_y = self.tile_map.sprite_lists[LAYER_NAME_PLAYER][0].center_y
        self.player.center_x, self.player.center_y = (player_x, player_y)
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player)

        # Set up enemies
        self.draw_enemies()

        # Physics :(
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, walls=self.scene[LAYER_NAME_BARRIER])

    def on_draw(self):
        # Clear the screen to the background color
        self.clear()

        # Draw our seen screen
        self.scene.draw()
        self.camera.use()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = self.player.speed
        elif key == arcade.key.S:
            self.player.change_y = -self.player.speed
        elif key == arcade.key.A:
            self.player.change_x = -self.player.speed
        elif key == arcade.key.D:
            self.player.change_x = self.player.speed

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = 0
        elif key == arcade.key.S:
            self.player.change_y = 0
        elif key == arcade.key.A:
            self.player.change_x = 0
        elif key == arcade.key.D:
            self.player.change_x = 0

    def draw_enemies(self):
        for monster_data in enemy_data.values():
            for monster in self.tile_map.sprite_lists[monster_data['layer']]:
                enemy = Enemy(monster_data['filename'], ENTITY_SIZE)
                enemy.center_x, enemy.center_y = monster.center_x, monster.center_y
                self.scene.add_sprite(LAYER_NAME_ENEMY, enemy)

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

    def on_update(self, delta_time):
        self.player.update()
        self.player.get_status()
        self.player.animation()
        self.physics_engine.update()
        self.center_camera_to_player()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
