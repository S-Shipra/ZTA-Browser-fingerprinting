from cryptography.fernet import Fernet
from flask import current_app

def get_cipher():
    key = current_app.config['FERNET_KEY'].encode()
    return Fernet(key)

def encrypt_data(data: str):
    cipher = get_cipher()
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(data: str):
    cipher = get_cipher()
    return cipher.decrypt(data.encode()).decode()