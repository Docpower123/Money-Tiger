import arcade

# Set up the window with hardware acceleration enabled
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Hardware acceleration example"
arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, True)

# Draw a rectangle using hardware acceleration
def draw_rectangle():
    arcade.draw_lrtb_rectangle_filled(100, 200, 500, 400, arcade.color.RED)

# Draw the rectangle
def on_draw():
    arcade.start_render()
    draw_rectangle()

# Run the game
arcade.schedule(on_draw, 1 / 60)
arcade.run()
