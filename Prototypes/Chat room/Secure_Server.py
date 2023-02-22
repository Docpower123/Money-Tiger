import socket
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Generate RSA key pair
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Serialize public key
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Set up server
server_address = ('localhost', 10000)
buffer_size = 4096

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
    server_socket.bind(server_address)

    print(f'Server is listening on {server_address}')

    while True:
        data, client_address = server_socket.recvfrom(buffer_size)

        # Decrypt data using private key
        decrypted_data = private_key.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        print(f'Received data from {client_address}: {decrypted_data.decode()}')

        # Encrypt response using client public key
        response = b'Hello, client!'
        encrypted_response = public_key.encrypt(
            response,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        server_socket.sendto(encrypted_response, client_address)
