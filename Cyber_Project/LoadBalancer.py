from socket import *
from settings import *
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

clients = []
slaves = []

# parameters for the server to use
HOST = LB_IP
PORT = LB_PORT
ADDR = (HOST, PORT)


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


def receive_message(server_socket, private_key, public_key):
    data, client_address = server_socket.recvfrom(RECV_SIZE)
    signature, encrypted_message = data[:256], data[256:]
    try:
        public_key.verify(
            signature,
            encrypted_message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except:
        print("Invalid signature")
        server_socket.close()
        exit()
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message, client_address


def send_response(server_socket, response, public_key, private_key, client_address):
    encrypted_response = public_key.encrypt(
        response,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    signature = private_key.sign(
        encrypted_response,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    server_socket.sendto(signature + encrypted_response, client_address)


def handle_new_user(addr):
    """
    code to find out the best server
    """
    print('new client!', addr)
    server = slaves[0]
    send_response(loadbalancer, f'{server}'.encode(), public_key, private_key, addr)
    send_response(loadbalancer, f'IP{addr}'.encode(), public_key, private_key, server)


# Load the private key from the PEM encoded file
private_key = load_private_key("private_key.pem")
# Load the public key from the PEM encoded file
public_key = load_public_key("public_key.pem")
# setting up the server
loadbalancer = socket(AF_INET, SOCK_DGRAM)
loadbalancer.bind(ADDR)
print('load balancer is up and running!')

# set up connection with slaves
count = 0
while True:
    data, addr = receive_message(loadbalancer, private_key, public_key)
    if str(addr[1]).startswith('9'):
        slaves.append(addr)
        send_response(loadbalancer, f'done'.encode(), public_key, private_key, addr)
        count += 1
    if count == 1:
        break

while True:
    # begin work with clients:
    data, addr = receive_message(loadbalancer, private_key, public_key)
    if addr not in clients and addr not in slaves:
        clients.append(addr)
        handle_new_user(addr)


# ------------------- to fix / to add -------------------
# enemies move weird + takes time to move from 0,0


# Structure: (USERNAME,TYPE,DATA)
# Types:
    # PSS - POSITION STATUS STATS - DATA=player(x,y,status,health)+enemies(x,y,status,health,index)
    # MDROP - make drops - DATA=(drop_name,x,y, drop_status)
    # PDROP - pick drops - DATA=(drop_name,x,y)
    # WAT - weapon attack - DATA=(player_x,player_y,status,name)
    # MAT - magic attack - DATA=(magic_x,magic_y,status,name)
    # HURT - enemies hurt - DATA=(enemy_index,player_damage)
    # KILL - client is no more in game - DATA=(username)
    # LOG - client logged in - DATA=(username)
    # MSG - client sent message - DATA(message)
