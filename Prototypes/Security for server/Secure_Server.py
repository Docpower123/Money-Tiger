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


def receive_message(server_socket, private_key, public_key):
    data, client_address = server_socket.recvfrom(1024)
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


def run_server():
    # Load the private key from the PEM encoded file
    private_key = load_private_key("private_key.pem")

    # Load the public key from the PEM encoded file
    public_key = load_public_key("public_key.pem")

    # Create a UDP socket and bind it to a port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 1234))

    # Receive and send messages indefinitely
    while True:
        # Receive an encrypted message from the client
        decrypted_message, client_address = receive_message(server_socket, private_key, public_key)
        print("Received message:", decrypted_message.decode())

        # Encrypt and send a response to the client
        response = b"Thank you for your message!"
        send_response(server_socket, response, public_key, private_key, client_address)

    # Close the socket
    server_socket.close()


if __name__ == '__main__':
    run_server()
