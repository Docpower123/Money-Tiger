import socket
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

def run_client():
    # Load the private key from the PEM encoded file
    private_key = load_private_key("private_key.pem")

    # Load the public key from the PEM encoded file
    public_key = load_public_key("public_key.pem")

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send a message to the server
    message = b"Hello, server!"
    server_address = ('localhost', 1234)
    send_message(client_socket, message, public_key, private_key, server_address)
    print("Sent message:", message.decode())

    # Receive a response from the server
    response, server_address = receive_response(client_socket, private_key, public_key)
    print("Received response:", response.decode())

    # Close the socket
    client_socket.close()

if __name__ == '__main__':
    run_client()
