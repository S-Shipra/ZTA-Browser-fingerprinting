import hmac
import hashlib
import json
from flask import current_app

def generate_hmac(data: dict):
    secret = current_app.config['SECRET_KEY']

    message = json.dumps(data, sort_keys=True).encode()

    return hmac.new(
        secret.encode(),
        message,
        hashlib.sha256
    ).hexdigest()


def verify_hmac(data: dict, received_hmac: str):
    calculated = generate_hmac(data)
    return hmac.compare_digest(calculated, received_hmac)