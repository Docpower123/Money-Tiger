import socket
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Generate client RSA key pair
client_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
client_public_key = client_private_key.public_key()

# Load server public key from file
with open("public.pem", "rb") as key_file:
    server_public_key = serialization.load_pem_public_key(
        key_file.read(),
    )

# Set up socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 5001))

# Send message to server
message = {
    'public_key': client_public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).hex(),
    'data': "Hello, world!",
    'signature': client_private_key.sign(
        "Hello, world!".encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    ).hex()
}
print(f"Sending message: {message}")
data = json.dumps(message).encode()
client_socket.send(data)

# Receive challenge from server
data = client_socket.recv(1024)
print(f"Received data: {data}")
message = json.loads(data)
challenge = message['challenge']
print(f"Received challenge: {challenge}")

# Send response to server
response = client_private_key.encrypt(
    challenge.encode(),
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
).hex()
message = {
    'response': response
}
print(f"Sending response: {message}")
client_socket.send(json.dumps(message).encode())

# Close connection
client_socket.close()
