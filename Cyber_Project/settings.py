import os.path

IP = '192.168.173.20'

# Load Balancer
LB_IP = IP
LB_PORT = 9999

# Slave 1
S1_IP = IP
S1_PORT = 9994

# Game
FEMALE_IP = IP
FEMALE_PORT = 6705

# Game1
MALE_IP = IP
MALE_PORT = 6604

# Generally game
SPRITE_SCALING = 1
SCREEN_COLOR = (113, 221, 238)
SCREEN_WIDTH = 650
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Money Tiger"
TILED_MAP = './map/bestmap.json'

# music!
DEFAULT_MUSIC = './audio/never.mp3'
POTION_MUSIC = './audio/gimme.mp3'
POTION1_MUSIC = './audio/goni.ogg'


# entity
ENTITY_SIZE = 1

# player
DEFAULT_ITEM = 'eraser'
PLAYER_IMAGE_SIZE = 64
PLAYER_IMAGE = './graphic/player/down/down_0.png'
PLAYER_PATH = './graphic/player/'
player_animations = {'up': ['up_0.png', 'up_1.png', 'up_2.png', 'up_3.png'],
                     'down': ['down_0.png', 'down_1.png', 'down_2.png', 'down_3.png'],
                     'left': ['left_0.png', 'left_1.png', 'left_2.png', 'left_3.png'],
                     'right': ['right_0.png', 'right_1.png', 'right_2.png', 'right_3.png'],
                     'right_idle': ['right_idle.png'], 'left_idle': ['left_idle.png'],
                     'up_idle': ['up_idle.png'], 'down_idle': ['down_idle.png'],
                     'right_attack': ['right_attack.png'], 'left_attack': ['left_attack.png'],
                     'up_attack': ['up_attack.png'], 'down_attack': ['down_attack.png']}

# enemy
ENEMY_PATH = './graphic/monsters/'
enemy_data = {'Squid': {'health': 100, 'layer': 'Squid', 'damage': 20, 'drop': ['eraser', 'heal', 'potion', 'potion1'], 'filename': './graphic/monsters/Squid/idle/0.png', 'attack_radius': 80, 'notice_radius': 300},
              'Bamboo': {'health': 70, 'layer': 'Bamboo', 'damage': 6, 'drop': ['eraser', 'heal', 'potion', 'potion1'], 'filename': './graphic/monsters/Bamboo/idle/0.png', 'attack_radius': 80, 'notice_radius': 300},
              'Raccoon': {'health': 300, 'layer': 'Raccoon', 'damage': 40, 'drop': ['eraser', 'heal', 'potion', 'potion1'], 'filename': './graphic/monsters/Raccoon/idle/0.png', 'attack_radius': 180, 'notice_radius': 400},
              'Spirit': {'health': 100, 'layer': 'Spirit', 'damage': 8, 'drop': ['eraser', 'heal', 'potion', 'potion1'], 'filename': './graphic/monsters/Spirit/idle/0.png', 'attack_radius': 130, 'notice_radius': 300}}
raccoon_animations = {'attack': ['0.png', '1.png', '2.png', '3.png'],
                      'idle': ['0.png', '1.png', '2.png', '3.png', '4.png', '5.png'],
                      'move': ['0.png', '1.png', '2.png', '3.png', '4.png']}
squid_animations = {'attack': ['0.png'],
                    'idle': ['0.png', '1.png', '2.png', '3.png', '4.png'],
                    'move': ['0.png', '1.png', '2.png', '3.png']}
spirit_bamboo_animations = {'attack': ['0.png'],
                            'idle': ['0.png', '1.png', '2.png', '3.png'],
                            'move': ['0.png', '1.png', '2.png', '3.png']}

# weapon
DEFAULT_WEAPON = 'sword'
weapon_data = {
    'sword': {'cooldown': 0.1, 'damage': 15, 'graphic': './graphics/weapons/sword/full.png'},
    'lance': {'cooldown': 0.5, 'damage': 30, 'graphic': './graphics/weapons/lance/full.png'},
    'axe': {'cooldown': 0.7, 'damage': 20, 'graphic': './graphics/weapons/axe/full.png'},
    'rapier': {'cooldown': 0.3, 'damage': 8, 'graphic': './graphics/weapons/rapier/full.png'},
    'sai': {'cooldown': 0.2, 'damage': 10, 'graphic': './graphics/weapons/sai/full.png'}}

# magic
DEFAULT_MAGIC = 'flame'
magic_data = {
    'flame': {'strength': 0, 'cost': 20, 'graphic': './graphic/particles/flame/fire.png'},
    'heal': {'strength': 20, 'cost': 10, 'graphic': './graphic/particles/heal/heal.png'},
    'potion': {'strength': 0, 'cost': 15, 'graphic': './graphic/particles/heal/heal.png'},  # gimme more
    'potion1': {'strength': 0, 'cost': 15, 'graphic': './graphic/particles/heal/heal.png'}}  # goni says "where" for 20 min

# drops & inventory
UI_SIZE = 14
ROW_SIZE = 5
THROW_DISTANCE = 60
drop_data = {
    'eraser': {'amount': 1, 'type': 'drop', 'graphic': './graphic/drops/eraser.png'},
    'heal': {'amount': 1, 'type': 'magic', 'graphic': './graphic/magic/heal/heal.png'},
    'potion': {'amount': 1, 'type': 'magic', 'graphic': './graphic/drops/potion.png'},
    'potion1': {'amount': 1, 'type': 'magic', 'graphic': './graphic/drops/potion1.png'}}

# tile
TILE_SIZE = 0.7

# TileMap
LAYER_NAME_GROUND = "Ground"
LAYER_NAME_BARRIER = "Barrier"
LAYER_NAME_ITEM = "Item"
LAYER_NAME_ENTITY = "Entity"
LAYER_OPTIONS = {
    LAYER_NAME_GROUND: {"use_spatial_hash": True},
    LAYER_NAME_BARRIER: {"use_spatial_hash": True},
    LAYER_NAME_ITEM: {"use_spatial_hash": True},
    LAYER_NAME_ENTITY: {"use_spatial_hash": True}}
