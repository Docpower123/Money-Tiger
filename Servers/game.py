import arcade
from socket import *

# parameters for the server to use
HOST = '192.168.1.161'
PORT = 6777
ADDR = (HOST, PORT)
Server_ADDR = ('192.168.1.161', 9999)

# setting up the server
game = socket(AF_INET, SOCK_DGRAM)
game.bind(ADDR)
game.sendto(f'{ADDR}'.encode(), Server_ADDR)
while True:
    data, addr = game.recvfrom(1024)
    if data.decode():
        Server_ADDR = data.decode()
        Server_ADDR = eval(Server_ADDR)
        break

print(Server_ADDR)
print(isinstance(Server_ADDR, tuple))

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Move Sprite with Keyboard Example"

MOVEMENT_SPEED = 5



class Player(arcade.Sprite):
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1
        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1



class MyGame(arcade.Window):
    """
    Main application class.
    """

    def _init_(self, width, height, title):
        """
        Initializer
        """

        # Call the parent class initializer
        super()._init_(width, height, title)

        # Variables that will hold sprite lists
        self.player_list = None

        # Set up the player info
        self.player_sprite = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(":resources:images/animated_characters/female_person/"
                                    "femalePerson_idle.png", SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """


        # Move the player

        self.player_list.update()
        game.sendto(f'{self.player_sprite.center_x}, {self.player_sprite.center_y}'.encode(), Server_ADDR)
        print(self.player_sprite.center_x)
        print(self.player_sprite.center_y)
        while True:
            data, addr = game.recvfrom(1024)
            if data.decode():
                cords = data.decode().split(',')
                self.player_sprite.center_x = int(cords[0])
                self.player_sprite.center_y = int(cords[1])
                break


    def on_key_press(self, key, modifiers):

        """Called whenever a key is pressed. """



        # If the player presses a key, update the speed

        if key == arcade.key.UP:

            self.player_sprite.change_y = MOVEMENT_SPEED

        elif key == arcade.key.DOWN:

            self.player_sprite.change_y = -MOVEMENT_SPEED

        elif key == arcade.key.LEFT:

            self.player_sprite.change_x = -MOVEMENT_SPEED

        elif key == arcade.key.RIGHT:

            self.player_sprite.change_x = MOVEMENT_SPEED



    def on_key_release(self, key, modifiers):

        """Called when the user releases a key. """



        # If a player releases a key, zero out the speed.

        # This doesn't work well if multiple keys are pressed.

        # Use 'better move by keyboard' example if you need to

        # handle this.

        if key == arcade.key.UP or key == arcade.key.DOWN:

            self.player_sprite.change_y = 0

        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:

            self.player_sprite.change_x = 0



def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()