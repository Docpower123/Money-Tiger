from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

with open('Cyber_Project/public.pem', 'rb') as f:  # Open file in binary mode
    key_bytes = f.read()

# Load the public key from the bytes using the PEM format
public_key = serialization.load_pem_public_key(key_bytes)

def encyrpt_data(info):
    # Encrypt data using the public key
    data = info.encode()
    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data


def decrypt_data(info):
    # The decryption code should use a private key, not the public key bytes
    with open('Cyber_Project/private.pem', 'rb') as f:
        private_key_bytes = f.read()
        private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    decrypted_data = private_key.decrypt(
        info,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data.decode()


encrypted_data = encyrpt_data('hoiiii')
print(f"Encrypted data: {encrypted_data}")

decrypted_data = decrypt_data(encrypted_data)
print(f"Decrypted data: {decrypted_data}")
