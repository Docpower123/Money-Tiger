import socket
import time
import threading
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes


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
    data, server_address = client_socket.recvfrom(1024)
    print(data)
    print(server_address)
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



# Load the private key from the PEM encoded file
private_key = load_private_key("private_key.pem")
# Load the public key from the PEM encoded file
public_key = load_public_key("public_key.pem")
# Create a UDP socket and bind it to a specific address and port
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
player_coords = '200, 100'
send_message(client, f'coords:{player_coords}'.encode(), public_key, private_key, ('localhost', 9000))


while True:
    data, addr = receive_response(client, private_key, public_key)
    print(data)
    send_message(client, f'hello!'.encode(), public_key, private_key, ('localhost', 9000))
    msg = f'a,DBG,Password,a'
    send_message(client, msg.encode(), public_key, private_key, ('localhost', 9000))