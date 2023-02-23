import socket
from cryptography.hazmat.primitives.asymmetric import padding
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

# Create a UDP socket and connect it to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.connect(('localhost', 1234))

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
client_socket.send(signature + encrypted_message)

# Receive and decrypt the response from the server
data = client_socket.recv(1024)
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
print("Received response:", decrypted_response.decode())

# Close the socket
client_socket.close()
