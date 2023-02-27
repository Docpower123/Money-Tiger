import socket
import hmac
import hashlib
from base64 import b64encode
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes


# Set up the UDP socket
HOST = 'localhost'
PORT = 5003
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('localhost', 0))

# Generate a new RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# Define the shared secret key
SECRET_KEY = b'my_secret_key'

# Define a blacklist of clients by their IP addresses
BLACKLIST = set()

while True:
    print(BLACKLIST)
    # Receive a message from the server
    data, addr = s.recvfrom(1024)
    print(data)
    # Check if the client is blacklisted
    if addr in BLACKLIST:
        print(f'{addr} is blacklisted')
        continue

    # Extract the HMAC digest and message from the received data
    received_digest = data[:32]
    message = data[32:]

    # Compute the HMAC digest of the message
    computed_digest = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()

    # Verify that the received digest matches the computed digest
    if received_digest == computed_digest:
        # If the digests match, send a response back to the server
        good_message = b'This is a good message.'
        good_signature = private_key.sign(good_message, padding.PKCS1v15(), hashes.SHA256())
        good_response = {
            'message': good_message,
            'signature': good_signature,
            'public_key': public_key,
        }
        good_response_data = b64encode(str(good_response).encode())
        s.sendto(good_response_data, addr)
        print(f'Sent good response to {addr}')

        bad_message = b'This message is invalid!'
        bad_signature = private_key.sign(bad_message, padding.PKCS1v15(), hashes.SHA256())
        bad_response = {
            'message': bad_message,
            'signature': bad_signature,
            'public_key': public_key,
        }
        bad_response_data = b64encode(str(bad_response).encode())
        s.sendto(bad_response_data, addr)
        print(f'Sent bad response to {addr}')
    else:
        # If the digests don't match, blacklist the client and send a response
        print(f'Invalid message received from {addr}')
        BLACKLIST.add(addr)
        s.sendto(b'You have been blacklisted', addr)
