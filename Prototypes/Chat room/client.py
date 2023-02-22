import socket
import hmac
import hashlib

# Set up the UDP socket
HOST = 'localhost'
PORT = 5002
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define the shared secret key
SECRET_KEY = b'my_secret_key'

# Define the message to send
message = 'Hello, server!'.encode()


def auth(message):
    # Compute the HMAC digest of the message
    digest = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()
    return digest + message


newtext = auth(message)
# Send the message and HMAC digest to the server
s.sendto(newtext, (HOST, PORT))
print(f'Sent message to server: {message.decode()}')

# Receive the response from the server
response, addr = s.recvfrom(1024)

# Verify the HMAC digest of the response
received_digest = response[:32]
response_message = response[32:]
computed_digest = hmac.new(SECRET_KEY, response_message, hashlib.sha256).digest()

if received_digest == computed_digest:
    # If the digests match, print the response
    print(f'Received response from server: {response_message.decode("latin-1")}')
else:
    # If the digests don't match, print an error message
    print('Invalid response received from server')

# Send an incorrect message to the server
s.sendto(b'Incorrect message', (HOST, PORT))

# Receive the response from the server
response, addr = s.recvfrom(1024)

# Check if the client is blacklisted
if response == b'You have been blacklisted':
    print(f'Blacklisted by server')
else:
    print(f'Received response from server: {response.decode("latin-1")}')
