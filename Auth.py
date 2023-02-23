import socket
import threading
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.primitives import serialization, hashes

# Load the private key from the PEM encoded file
with open("private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )

# Load the public key from the PEM encoded file
with open("public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

# Create a UDP socket and bind it to a port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 1234))

# Define a function to handle incoming messages
def handle_message(data, address):
    # Verify the message signature using the public key
    signature, message = data[:256], data[256:]
    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            utils.Prehashed(hashes.SHA256())
        )
    except:
        print("Invalid signature")
        return

    # Decrypt the message using the private key
    decrypted_message = private_key.decrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Do something with the decrypted message
    print("Received message:", decrypted_message.decode())

# Define a function to receive incoming messages and handle them in a separate thread
def receive_messages():
    while True:
        data, address = server_socket.recvfrom(1024)
        threading.Thread(target=handle_message, args=(data, address)).start()

# Start receiving messages in a separate thread
threading.Thread(target=receive_messages).start()

# Send an encrypted message to the server
message = b"Hello, world!"
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
server_socket.sendto(signature + encrypted_message, ('localhost', 1234))
