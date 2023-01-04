# screen
SCEEN_COLOR = (113, 221, 238)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "urmom"
TILE_MAP = './map/map.json'

# entity
ENTITY_SIZE = 1
ENEMY_PATH = './graphic/monsters/'
animations = {'up': ['up_0.png', 'up_1.png', 'up_2.png', 'up_3.png'],
              'down': ['down_0.png', 'down_1.png', 'down_2.png', 'down_3.png'],
              'left': ['left_0.png', 'left_1.png', 'left_2.png', 'left_3.png'],
              'right': ['right_0.png', 'right_1.png', 'right_2.png', 'right_3.png'],
              'right_idle': ['right_idle.png'], 'left_idle': ['left_idle.png'],
              'up_idle': ['up_idle.png'], 'down_idle': ['down_idle.png'],
              'right_attack': [], 'left_attack': [],
              'up_attack': [], 'down_attack': []}

# player
PLAYER_START_CORDS = (800, 800)
PLAYER_SPEED = 3
PLAYER_IMAGE = './graphic/player/down/down_0.png'
PLAYER_PATH = './graphic/player/'

# enemy
enemy_data = {'squid': {'layer': 'Squid', 'filename': './graphic/monsters/squid/idle/0.png'},
              'bamboo': {'layer': 'Bamboo', 'filename': './graphic/monsters/bamboo/idle/0.png'},
              'raccoon': {'layer': 'Raccoon', 'filename': './graphic/monsters/raccoon/idle/0.png'},
              'spirit': {'layer': 'Spirit', 'filename': './graphic/monsters/spirit/idle/0.png'}}

# tile
TILE_SIZE = 0.7

# TileMap
LAYER_NAME_GROUND = "Ground"
LAYER_NAME_PLANTS_AND_ROCKS = "Plants and Rocks"
LAYER_NAME_BARRIER = "Barrier"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMY = "Enemy"
LAYER_OPTIONS = {
    LAYER_NAME_GROUND: {"use_spatial_hash": True},
    LAYER_NAME_PLANTS_AND_ROCKS: {"use_spatial_hash": True},
    LAYER_NAME_BARRIER: {"use_spatial_hash": True}}
