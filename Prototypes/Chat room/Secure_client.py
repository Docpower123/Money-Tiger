import socket
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import padding, utils
from cryptography.hazmat.primitives import serialization

# Set up the UDP socket
HOST = 'localhost'
PORT = 5002
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Load the private key from file
with open('private.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Define a message to send to the server
message = 'Hello, server! This is a test message.'.encode()

# Compute the HMAC digest of the message
digest = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()

# Sign the message using the private key
signature = private_key.sign(
    message,
    padding.PKCS1v15(),
    utils.Prehashed(hashes.SHA256())
)

# Concatenate the HMAC digest, message, and signature into a single message
data = digest + message + signature

# Send the message to the server
s.sendto(data, (HOST, PORT))

# Receive a response from the server
data, addr = s.recvfrom(1024)

# Extract the HMAC digest and message from the received data
received_digest = data[:32]
message = data[32:]

# Compute the HMAC digest of the message
computed_digest = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()

# Verify that the received digest matches the computed digest
if received_digest == computed_digest:
    # If the digests match, print the response from the server
    print(f'Response from server: {message.decode()}')
else:
    # If the digests don't match, print an error message
    print('Invalid response received from server')
