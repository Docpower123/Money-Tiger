import socket
import hmac
import hashlib
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Set up the UDP socket
HOST = 'localhost'
PORT = 5003
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
print(f'Server listening on {HOST}:{PORT}')

# Load the public key for message verification
with open('public_key.pem', 'rb') as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=None
    )

# Define the shared secret key
SECRET_KEY = b'my_secret_key'

# Define a blacklist of clients by their IP addresses
BLACKLIST = set()

while True:
    print(BLACKLIST)
    # Receive a message from the client
    data, addr = s.recvfrom(1024)

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
        # If the digests match, verify the message signature
        signature = message[:256]
        message_body = message[256:]
        try:
            public_key.verify(signature, message_body, padding.PKCS1v15(), hashes.SHA256())
            # If the signature is verified, send a response back to the client
            response = f'Received {message.decode()} from {addr}'.encode()
            response_digest = hmac.new(SECRET_KEY, response, hashlib.sha256).digest()
            s.sendto(response_digest + response, addr)
            print(f'Sent response to {addr}: {response.decode()}')
        except:
            # If the signature verification fails, blacklist the client and send a response
            print(f'Invalid message received from {addr}')
            BLACKLIST.add(addr)
            s.sendto(b'You have been blacklisted', addr)
    else:
        # If the digests don't match, blacklist the client and send a response
        print(f'Invalid message received from {addr}')
        BLACKLIST.add(addr)
        s.sendto(b'You have been blacklisted', addr)
