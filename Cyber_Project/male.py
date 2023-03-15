import threading
import queue
import arcade
import time
import random
from socket import *
from settings import *
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from random import choice
from player import Player
from enemy import Enemy
from weapon import Weapon
from magic import Magic
from drop import Drop
from ui_screen import UI_SCREEN
from ui import UI
import tkinter
from tkinter import *
from tkinter import messagebox
import mysql.connector
from chat import run_chat


#connecting to the database
db = mysql.connector.connect(host="localhost",user="root",passwd="P123321p",database="dblogin")
mycur = db.cursor()

def error_destroy():
    err.destroy()

def succ_destroy():
    succ.destroy()
    root1.destroy()

def error():
    global err
    err = Toplevel(root1)
    err.title("Error")
    err.geometry("200x100")
    Label(err,text="All fields are required..",fg="red",font="bold").pack()
    Label(err,text="").pack()
    Button(err,text="Ok",bg="grey",width=8,height=1,command=error_destroy).pack()

def success():
    global succ
    succ = Toplevel(root1)
    succ.title("Success")
    succ.geometry("200x100")
    Label(succ, text="Registration successful...", fg="green", font="bold").pack()
    Label(succ, text="").pack()
    Button(succ, text="Ok", bg="grey", width=8, height=1, command=succ_destroy).pack()

def register_user():
    username_info = username.get()
    password_info = password.get()
    if username_info == "":
        error()
    elif password_info == "":
        error()
    else:
        sql = "insert into dblogin values(%s,%s)"
        t = (username_info, password_info)
        mycur.execute(sql, t)
        db.commit()
        Label(root1, text="").pack()
        time.sleep(0.50)
        global NAME
        NAME = username.get()
        success()

def registration():
    global root1
    root1 = Toplevel(root)
    root1.title("Registration")
    root1.geometry("300x250")
    global username
    global password
    Label(root1,text="Register your account",bg="grey",fg="black",font="bold",width=300).pack()
    username = StringVar()
    password = StringVar()
    Label(root1,text="").pack()
    Label(root1,text="Username :",font="bold").pack()
    Entry(root1,textvariable=username).pack()
    Label(root1, text="").pack()
    Label(root1, text="Password :").pack()
    Entry(root1, textvariable=password,show="*").pack()
    Label(root1, text="").pack()
    Button(root1,text="Register",bg="red",command=register_user).pack()

def login():
    global root2
    root2 = Toplevel(root)
    root2.title("Login")
    root2.geometry("300x300")
    global username_varify
    global password_varify
    Label(root2, text="Login", bg="grey", fg="black", font="bold",width=300).pack()
    username_varify = StringVar()
    password_varify = StringVar()
    Label(root2, text="").pack()
    Label(root2, text="Username :", font="bold").pack()
    Entry(root2, textvariable=username_varify).pack()
    Label(root2, text="").pack()
    Label(root2, text="Password :").pack()
    Entry(root2, textvariable=password_varify, show="*").pack()
    Label(root2, text="").pack()
    Button(root2, text="Login", bg="red",command=login_varify).pack()
    Label(root2, text="")

def logg_destroy():
    logg.destroy()
    root2.destroy()

def fail_destroy():
    fail.destroy()

def logged():
    global logg
    logg = Toplevel(root2)
    logg.title("Welcome")
    logg.geometry("200x100")
    Label(logg, text="Welcome {} ".format(username_varify.get()), fg="green", font="bold").pack()
    global NAME
    NAME = username_varify.get()
    Label(logg, text="").pack()
    Button(logg, text="Log-Out", bg="grey", width=8, height=1, command=logg_destroy).pack()


def failed():
    global fail
    fail = Toplevel(root2)
    fail.title("Invalid")
    fail.geometry("200x100")
    Label(fail, text="Invalid credentials...", fg="red", font="bold").pack()
    Label(fail, text="").pack()
    Button(fail, text="Ok", bg="grey", width=8, height=1, command=fail_destroy).pack()


def login_varify():
    user_varify = username_varify.get()
    pas_varify = password_varify.get()
    sql = "select * from dblogin where Username = %s and Password = %s"
    mycur.execute(sql,[(user_varify),(pas_varify)])
    results = mycur.fetchall()
    if results:
        for i in results:
            logged()
            break
    else:
        failed()


def db_get_info(info_name):
    user_varify = username_varify.get()
    pas_varify = password_varify.get()
    sql = f"select {info_name} from dblogin where Username = %s and Password = %s"
    mycur.execute(sql, [(user_varify), (pas_varify)])
    info = mycur.fetchall()
    return info[0][0]


def db_set_info(info_name, t):
    sql = f"update dblogin set {info_name} = %s where Username = %s"
    mycur.execute(sql, t)
    db.commit()


def main_screen():
    global root
    root = Tk()
    root.title("Login")
    root.geometry("300x300")
    Label(root,text="login",font="bold",bg="grey",fg="black",width=300).pack()
    Label(root,text="").pack()
    Button(root,text="Login",width="8",height="1",bg="red",font="bold",command=login).pack()
    Label(root,text="").pack()
    Button(root, text="Registration",height="1",width="15",bg="red",font="bold",command=registration).pack()
    Label(root,text="").pack()
    Label(root,text="").pack()


# security functions
def load_private_key(filename):
    with open(filename, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    return private_key


def load_public_key(filename):
    with open(filename, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key


def send_message(client_socket, message, public_key, private_key, server_address):
    encrypted_message = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    signature = private_key.sign(
        encrypted_message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    client_socket.sendto(signature + encrypted_message, server_address)


def receive_response(client_socket, private_key, public_key):
    data, server_address = client_socket.recvfrom(RECV_SIZE)
    signature, encrypted_response = data[:256], data[256:]
    try:
        public_key.verify(
            signature,
            encrypted_response,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except:
        print("Invalid signature")
        client_socket.close()
        exit()
    decrypted_response = private_key.decrypt(
        encrypted_response,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_response, server_address


# log in
main_screen()
root.mainloop()


# parameters for the server to use
ADDR = (MALE_IP, MALE_PORT)
Server_ADDR = (LB_IP, LB_PORT)
messages = queue.Queue()


# Load the private key from the PEM encoded file
private_key = load_private_key("private_key.pem")
# Load the public key from the PEM encoded file
public_key = load_public_key("public_key.pem")
# setting up the server
game = socket(AF_INET, SOCK_DGRAM)
game.bind(ADDR)
send_message(game, f'IP, {ADDR}'.encode(), public_key, private_key, Server_ADDR)
while True:
    data, addr = receive_response(game, private_key, public_key)
    if data.decode():
        Server_ADDR = data.decode()
        Server_ADDR = eval(Server_ADDR)
        break
print("connected")


def get_info():
    while True:
        data, addr = receive_response(game, private_key, public_key)
        messages.put((data, addr))


def chat():
    while True:
        run_chat(NAME)


t = threading.Thread(target=get_info)
t2 = threading.Thread(target=chat)
t.start()
t2.start()


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True, vsync=True)
        arcade.set_background_color(SCREEN_COLOR)

        # Screen
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(self.width, self.height)
        self.tile_map = arcade.load_tilemap(TILED_MAP, TILE_SIZE, layer_options=LAYER_OPTIONS)
        self.pss_msg = []
        self.pss_time = time.time()
        self.use_srgb = True

        # Sound
        self.sound = arcade.Sound(DEFAULT_MUSIC, streaming=True)
        self.volume = MUSIC_VOLUME
        self.player_sound = arcade.play_sound(self.sound, self.volume)

        # My Player
        self.player = Player(PLAYER_IMAGE, SPRITE_SCALING)
        self.player_physics_engine = None

        # Players Communication
        self.players = {NAME: self.player}
        self.player_list = arcade.SpriteList()
        self.drops_list = []
        self.drops_number = 0
        self.weapons_list = []
        self.weapons_number = 0
        self.magic_list = []
        self.magic_number = 0

        # Enemies
        self.enemies_list = []
        self.dead_enemies_list = []
        self.enemies_physics = []
        self.enemies_number = 0

        # Inventory
        self.ui_screen = UI_SCREEN(self.player)
        self.ui = UI(self.player)
        self.game_paused_ui = False
        self.selection = 'sword'

    # ------------------ set up ------------------

    def info_from_db(self):
        # Position
        player_pos = db_get_info('Pos')
        if player_pos is None:
            # saving position first time registered
            self.player.center_x, self.player.center_y = random.randint(SPAWN["left"], SPAWN["right"]), random.randint(
                SPAWN["down"],
                SPAWN["up"])
        else:
            # going to position in database
            self.player.center_x, self.player.center_y = (
            float(player_pos.split(',')[0]), float(player_pos.split(',')[1]))

        # Health
        player_health = db_get_info('Health')
        if player_health is not None:
            self.player.health = int(player_health.split(',')[0])

        # Energy
        player_energy = db_get_info('Energy')
        if player_energy is not None:
            self.player.energy = int(float(player_energy.split(',')[0]))

        # Items
        player_items = db_get_info('Items')
        if player_items is not None:
            player_items = player_items.split(',')
            for i in range(0, len(player_items), 2):
                name = player_items[i]
                amount = int(player_items[i+1])
                not_in_items = name not in self.player.items.keys()
                if not_in_items or self.player.items[name]['amount'] != amount:
                    if not_in_items: self.player.items[name] = {}
                    self.player.items[name].update(drop_data[name])
                    self.player.items[name]['amount'] = amount
                if i+2 >= len(player_items): break

        # Last attack
        player_last_attack = db_get_info('Lastattack')
        if player_last_attack is not None:
            player_last_attack = player_last_attack.split(',')
            self.player.weapon = player_last_attack[0]
            self.player.magic = player_last_attack[1]

    def setup(self):
        # Screen
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Player
        self.info_from_db()
        self.scene.add_sprite('Player', self.player)

        # pss sending
        pss = f'{NAME},PSS,{self.player.center_x},{self.player.center_y},{self.player.status},{self.player.health}'
        send_message(game, pss.encode(), public_key, private_key, Server_ADDR)

        # enemies
        self.draw_enemies()

        # Physics :(
        self.player_physics_engine = arcade.PhysicsEngineSimple(self.player, walls=self.scene[LAYER_NAME_BARRIER])

    def on_draw(self):
        # Clear the screen to the background color
        self.clear()

        # Draw our seen screen
        self.scene.draw()
        self.camera.use()

        # enemies health
        for monster in self.enemies_list:
            if monster.name != 'Raccoon':
                arcade.draw_text(monster.health, monster.center_x, monster.center_y + 34, arcade.color.BLACK, 14)
            else:
                arcade.draw_text(monster.health, monster.center_x, monster.center_y + 104, arcade.color.BLACK, 14)

        # players health
        for p_name, p_sprite in self.players.items():
            arcade.draw_text(p_name + "  " + str(p_sprite.health), p_sprite.center_x - 34, p_sprite.center_y + 34,
                             arcade.color.BLACK, 14)

        # inventory
        self.ui.display()
        if self.game_paused_ui:
            self.ui_screen.display(self.selection)

    def main_cooldowns(self):
        # the function name is pretty clear...
        current_time = time.time()

        if self.player.attacking:
            if current_time - self.player.attack_time >= weapon_data[self.player.weapon]['cooldown']:
                self.player.attacking = False
                self.destroy_attack()

        if self.player.magicing:
            if current_time - self.player.magic_time >= magic_data[self.player.magic]['cooldown']:
                self.player.magicing = False
                self.destroy_magic()

        for weapon in self.weapons_list:
            if current_time - weapon.time >= weapon_data[weapon.name]['cooldown']:
                weapon.kill()

        for magic in self.magic_list:
            if current_time - magic.time >= magic_data[magic.name]['cooldown']:
                magic.kill()

        if not self.player.vulnerable:
            if current_time - self.player.hurt_time >= 0.4:
                self.player.vulnerable = True

    def center_camera_to_player(self):
        # the function name is pretty clear...
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    # ------------------ key input ------------------

    def on_key_press(self, key, modifiers):
        # Don't move if attack
        if self.player.attacking or self.player.magicing:
            return
        # attack!
        if key == arcade.key.SPACE:
            self.create_attack()
        # magic
        elif key == arcade.key.M:
            self.create_magic()
        # auto movement
        elif key == arcade.key.P:
            self.player.auto_movement = not self.player.auto_movement
            if self.player.auto_movement is False:
                self.player.change_x, self.player.change_y = (0, 0)
        # Don't take inputs if on auto movement
        elif self.player.auto_movement:
            return
        # inputs
        elif key == arcade.key.W:
            self.player.change_y = self.player.speed
        elif key == arcade.key.S:
            self.player.change_y = -self.player.speed
        elif key == arcade.key.A:
            self.player.change_x = -self.player.speed
        elif key == arcade.key.D:
            self.player.change_x = self.player.speed

    def on_key_release(self, key, modifiers):
        # log out
        if key == arcade.key.ESCAPE:
            # tell server about log out
            send_message(game, f'{NAME},KILL,{NAME}'.encode(), public_key, private_key, Server_ADDR)
            # save stuff in database
            db_set_info('Pos', (f'{self.player.center_x},{self.player.center_y}', NAME))
            db_set_info('Health', (f'{self.player.health}', NAME))
            db_set_info('Energy', (f'{int(self.player.energy)}', NAME))
            items_data = f''
            for item_name, item_value in self.player.items.items():
                if item_value['amount'] != 'permanent':
                    items_data += f",{item_name},{item_value['amount']}"
            if items_data != f'':
                db_set_info('Items', (items_data[1:], NAME))
            db_set_info('Lastattack', (f'{self.player.weapon},{self.player.magic}', NAME))
            # quit
            arcade.close_window()
            quit("Logged out successfully")

        # regular movement
        elif key == arcade.key.W:
            self.player.change_y = 0
        elif key == arcade.key.S:
            self.player.change_y = 0
        elif key == arcade.key.A:
            self.player.change_x = 0
        elif key == arcade.key.D:
            self.player.change_x = 0

        # drops :P
        elif key == arcade.key.Q and self.player.item is not None:
            self.create_drop()
            for barrier in self.scene.get_sprite_list(LAYER_NAME_BARRIER):
                if arcade.check_for_collision(barrier, self.player.last_drop):
                    self.pick_up_drops(self.player.last_drop)
                    return

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
                    self.player.current_attack = Weapon((self.player.center_x, self.player.center_y), self.player.weapon, self.player.status)

                # magic
                elif list(self.player.items.values())[self.player.selection_index]['type'] == 'magic':
                    self.player.magic = list(self.player.items.keys())[self.player.selection_index]

                # drop
                elif list(self.player.items.values())[self.player.selection_index]['type'] == 'drop':
                    self.player.item = list(self.player.items.keys())[self.player.selection_index]

    # ------------------ player ------------------

    def auto_move(self):
        # the function name is pretty clear...
        current_time = time.time()

        if current_time - self.player.auto_movement_time >= 0.4:
            self.player.auto_movement_time = time.time()
            x, y = self.player.center_x, self.player.center_y
            for barrier in self.scene.get_sprite_list(LAYER_NAME_BARRIER):
                # check if can move left
                self.player.center_x -= 64
                if arcade.check_for_collision(barrier, self.player) and (-1, 0) in self.player.movement_options:
                    self.player.movement_options.remove((-1, 0))
                self.player.center_x = x

                # check if can move right
                self.player.center_x += 64
                if arcade.check_for_collision(barrier, self.player) and (1, 0) in self.player.movement_options:
                    self.player.movement_options.remove((1, 0))
                self.player.center_x = x

                # check if can move down
                self.player.center_y -= 64
                if arcade.check_for_collision(barrier, self.player) and (0, -1) in self.player.movement_options:
                    self.player.movement_options.remove((0, -1))
                self.player.center_y = y

                # check if can move up
                self.player.center_y += 64
                if arcade.check_for_collision(barrier, self.player) and (0, 1) in self.player.movement_options:
                    self.player.movement_options.remove((0, 1))
                self.player.center_y = y

        if current_time - self.player.auto_movement_time2 >= 1.5:
            self.player.auto_movement_time2 = time.time()
            self.player.movement_options = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(self.player.movement_options)

        # Move!
        self.player.change_x, self.player.change_y = self.player.movement_options[0]
        self.player.change_x *= self.player.speed
        self.player.change_y *= self.player.speed

    def check_if_attacked(self):
        # the function name is pretty clear...
        for monster in self.enemies_list:
            if monster.attacked == self.player:
                return True
        return False

    # ------------------ enemies ------------------

    def draw_enemies(self):
        # draw
        for i in range(ENEMIES_NUM):
            if i == 0:
                name = 'Raccoon'
            elif i < ENEMIES_NUM / 4:
                name = 'Squid'
            elif i < ENEMIES_NUM / 2:
                name = 'Spirit'
            else:
                name = 'Bamboo'
            enemy = Enemy(enemy_data[name]['filename'], ENTITY_SIZE, enemy_data[name]['layer'], self.player,
                          self.player_list, self.enemies_number)

            self.enemies_number += 1
            self.enemies_list.append(enemy)

            self.scene.add_sprite(LAYER_NAME_ENTITY, enemy)

        # physics
        for monster in self.enemies_list:
            enemies_collision = self.scene[LAYER_NAME_BARRIER]
            for other_enemy in self.enemies_list:
                if other_enemy == monster:
                    continue
                if other_enemy in enemies_collision:
                    continue
                enemies_collision.append(other_enemy)

            physics = arcade.PhysicsEngineSimple(monster, walls=enemies_collision)
            self.enemies_physics.append(physics)

    def enemies_update(self):
        # movement & health & death
        if self.enemies_list:
            for monster in self.enemies_list:
                # update
                monster.e_update()

    def damage_enemies(self):
        # the function name is pretty clear...
        for index, monster in enumerate(self.enemies_list):
            if arcade.check_for_collision(self.player.current_attack, monster) and monster.health > 0:
                msg = f"{NAME},HURT,{index},{self.player.stats['attack']}"
                send_message(game, msg.encode(), public_key, private_key, Server_ADDR)

    # ------------------ attack! ------------------

    def create_attack(self):
        # the function name is pretty clear...
        self.player.attack_time = time.time()
        self.player.current_attack = Weapon((self.player.center_x, self.player.center_y), self.player.weapon, self.player.status)
        self.scene.add_sprite(LAYER_NAME_ITEM, self.player.current_attack)
        self.player.attacking = True
        # WAT message
        wat = f'{NAME},WAT,{self.player.center_x},{self.player.center_y},{self.player.status},{self.player.weapon}'
        send_message(game, wat.encode(), public_key, private_key, Server_ADDR)

    def destroy_attack(self):
        # the function name is pretty clear...
        self.player.attacking = False
        self.player.current_attack.kill()
        self.damage_enemies()

    def damage_player(self):
        # the function name is pretty clear...
        if self.player.vulnerable:
            self.player.vulnerable = False
            self.player.hurt_time = time.time()
            for monster in self.enemies_list:
                if monster.status != 'attack' or monster.attacked != self.player:
                    continue
                elif self.player.health - enemy_data[monster.name]['damage'] <= 0:
                    self.player.health = 0
                elif self.player.health > 0:
                    self.player.health -= enemy_data[monster.name]['damage']
                else:
                    self.player.health = 0

    # ------------------ magic ------------------

    def create_magic(self):
        # the function name is pretty clear...
        self.player.magic_time = time.time()
        self.player.magicing = True
        self.player.current_magic = Magic((self.player.center_x, self.player.center_y), self.player.magic, self.player.status)
        if self.player.magic == 'potion':
            arcade.stop_sound(self.player_sound)
            self.sound = arcade.Sound(POTION_MUSIC, streaming=True)
            self.player_sound = arcade.play_sound(self.sound, self.volume)
        elif self.player.magic == 'potion1':
            arcade.stop_sound(self.player_sound)
            self.sound = arcade.Sound(POTION1_MUSIC, streaming=True)
            self.player_sound = arcade.play_sound(self.sound, self.volume)
        did_magic = self.player.magic_update(self.player.current_magic)
        if not did_magic: return
        self.scene.add_sprite(LAYER_NAME_ITEM, self.player.current_magic)
        # MAT message
        mat = f'{NAME},MAT,{self.player.current_magic.center_x},{self.player.current_magic.center_y},{self.player.status},{self.player.magic}'
        send_message(game, mat.encode(), public_key, private_key, Server_ADDR)
        # ui update
        self.player.ui_magic_update(self.ui_screen)

    def destroy_magic(self):
        # the function name is pretty clear...
        if self.player.magic == 'flame':
            for index, monster in enumerate(self.enemies_list):
                if arcade.check_for_collision(self.player.current_magic, monster) and monster.health > 0:
                    hurt = f"{NAME},HURT,{index},{self.player.stats['attack']}"
                    send_message(game, hurt.encode(), public_key, private_key, Server_ADDR)

        self.player.magicing = False
        self.player.current_magic.kill()

    # ------------------ drop ------------------

    def create_drop(self):
        # the function name is pretty clear...
        self.drops_number += 1
        drops_pos = (int(self.player.center_x), int(self.player.center_y))
        self.player.last_drop = Drop(self.player.item, drops_pos, self.player.status, self.drops_number)
        # sending MDROP msg
        msg = f'{NAME},MDROP,{self.player.item},{drops_pos},{self.player.status}'
        send_message(game, msg.encode(), public_key, private_key, Server_ADDR)
        # other stuff
        self.drops_list.append(self.player.last_drop)
        self.scene.add_sprite(LAYER_NAME_ITEM, self.player.last_drop)
        # reducing amount of drop
        self.player.items[self.player.item]['amount'] -= 1
        # amount is 0, this drop is no more
        if self.player.items[self.player.item]['amount'] == 0:
            self.player.items.pop(self.player.item, None)
            self.player.item = None
            self.ui_screen.attribute_index -= 1

    def pick_up_drops(self, drop):
        # the function name is pretty clear...
        if drop.name in self.player.items.keys():
            #  increasing the amount of this drop - player pick up! :)
            self.player.items[drop.name]['amount'] += 1
        else:
            #  adding this drop to player's items list
            self.player.items[drop.name] = {}
            self.player.items[drop.name].update(drop_data[drop.name])
            self.ui_screen.attribute_index += 1
        # send info to server
        msg = f'{NAME},PDROP,{drop.name},{drop.pos}'
        send_message(game, msg.encode(), public_key, private_key, Server_ADDR)
        # this drop is no more on the floor :(
        drop.kill()
        self.drops_number -= 1
        self.drops_list.remove(drop)

    def check_if_pick_up_drops(self):
        # the function name is pretty clear...
        for drop in self.drops_list:
            if arcade.check_for_collision(self.player, drop):
                self.pick_up_drops(drop)

    # ------------------ update ------------------

    def read_pss_msg(self):
        # Players
        name = self.pss_msg[0]
        if name not in list(self.players.keys()): return
        if name != NAME:
            other_player = self.players[name]
            cords = self.pss_msg[2], self.pss_msg[3]
            if int(float(cords[0])) != other_player.center_x or int(float(cords[1])) != other_player.center_y:
                other_player.center_x = int(float(cords[0]))
                other_player.center_y = int(float(cords[1]))
            status = self.pss_msg[4]
            if other_player.status != status:
                other_player.status = status
            health = self.pss_msg[5]
            if other_player.health != health:
                other_player.health = health

        # Enemies
        if len(self.pss_msg) < 7 or not self.enemies_list: return
        index = 6
        for enemy_list_index, enemy in enumerate(self.enemies_list):
            enemy_pkt_index = self.pss_msg[index + 4]
            if int(enemy_pkt_index) != enemy_list_index: continue

            cords = float(self.pss_msg[index][1:]), float(self.pss_msg[index + 1][1:self.pss_msg[index + 1].find(')')])
            status = self.pss_msg[index + 2]
            health = int(float(self.pss_msg[index + 3]))
            enemy.status = status
            enemy.center_x, enemy.center_y = cords
            enemy.health = health
            if index + 5 > len(self.pss_msg) - 1:
                return
            index += 5

    def send_stuff(self):
        # PSS
        pss = f'{NAME},PSS,{self.player.center_x},{self.player.center_y},{self.player.status},{self.player.health}'
        send_message(game, pss.encode(), public_key, private_key, Server_ADDR)

    def on_update(self, delta_time):
        # Music!
        if self.player_sound.time == 0:
            self.player_sound = arcade.play_sound(self.sound, self.volume)

        # Screen
        self.main_cooldowns()
        self.center_camera_to_player()

        # Players
        self.player_list.update()

        # My Player
        if not self.player.attacking and not self.player.magicing:
            self.player_physics_engine.update()
        if self.player.auto_movement:
            self.auto_move()
        if self.check_if_attacked():
            self.damage_player()
        self.player.get_status()
        self.player.update()
        if len(self.player.items.keys()) < UI_SIZE:
            self.check_if_pick_up_drops()

        # Enemies
        for physics in self.enemies_physics:
            physics.update()
        self.enemies_update()

        # Receive info
        if self.pss_msg:
            self.read_pss_msg()
        if time.time() - self.pss_time >= PSS_COOLDOWN:
            self.pss_time = time.time()
            self.send_stuff()
        if not messages.empty():
            data, addr = messages.get()
            data = data.decode().split(',')
            name = data[0]
            type = data[1]

            if type == 'PSS':
                self.pss_msg = data

            elif type == 'LOG':
                for i in range(2, len(data)):
                    username = data[i]
                    self.players.update({username: Player(PLAYER_IMAGE, SPRITE_SCALING)})
                    self.player_list.append(self.players[username])
                    walls = self.player_physics_engine.walls[0]
                    walls.append(self.players[username])
                    self.player_physics_engine = arcade.PhysicsEngineSimple(self.player, walls=walls)
                    self.scene.add_sprite(LAYER_NAME_ENTITY, self.players[username])

            elif type == 'KILL':
                username = data[2]
                self.players[username].kill()
                self.players.pop(username)

            elif type == 'WAT' and name != NAME:
                cords = (int(float(data[2])), int(float(data[3])))
                p_status = data[4]
                weapon_name = data[5]

                self.weapons_number += 1
                weapon = Weapon(cords, weapon_name, p_status)
                weapon.time = time.time()
                self.weapons_list.append(weapon)
                self.scene.add_sprite(LAYER_NAME_ITEM, weapon)

            elif type == 'MAT' and name != NAME:
                cords = (int(float(data[2])), int(float(data[3])))
                p_status = data[4]
                magic_name = data[5]

                self.magic_number += 1
                magic = Magic(cords, magic_name, p_status)
                if magic.name in ('potion', 'potion1'):
                    magic.scale = 0.2
                magic.time = time.time()
                self.magic_list.append(magic)
                self.scene.add_sprite(LAYER_NAME_ITEM, magic)

            elif type == 'MDROP' and name != NAME:
                self.drops_number += 1
                drop_name, drop_status = data[2], data[5]
                drop_pos = (int(float(data[3][1:])),
                            int(float(data[4][1:data[4].find(')')])))
                drop = Drop(drop_name, drop_pos, drop_status, self.drops_number)
                self.drops_list.append(drop)
                self.scene.add_sprite(LAYER_NAME_ITEM, drop)

            elif type == 'PDROP' and name != NAME:
                drop_name = data[2]
                drop_pos = (int(float(data[3][1:])),
                            int(float(data[4][1:data[4].find(')')])))
                for drop in self.drops_list:
                    if drop.name != drop_name:
                        continue
                    if drop.pos == drop_pos:
                        drop.kill()
                        self.drops_number -= 1
                        self.drops_list.remove(drop)


# game
window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, NAME)
window.setup()
arcade.run()
game.close()
