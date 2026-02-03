from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import base64




def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    return private_key, private_key.public_key()


def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def load_public_key(pem: str):
    return serialization.load_pem_public_key(pem.encode())




def generate_aes_key():
    return Fernet.generate_key()


def encrypt_message(aes_key, message: str) -> bytes:
    return Fernet(aes_key).encrypt(message.encode())


def decrypt_message(aes_key, encrypted: bytes) -> str:
    return Fernet(aes_key).decrypt(encrypted).decode()




def encrypt_aes_key_with_rsa(aes_key, public_key):
    encrypted = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted)


def decrypt_aes_key_with_rsa(encrypted_b64, private_key):
    encrypted = base64.b64decode(encrypted_b64)
    return private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
