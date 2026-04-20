import hmac
import hashlib
import json
from flask import current_app
def deep_sort(obj):
    if isinstance(obj, dict):
        return {k: deep_sort(obj[k]) for k in sorted(obj)}
    elif isinstance(obj, list):
        return [deep_sort(i) for i in obj]
    else:
        return obj


def stable_json(data):
    sorted_data = deep_sort(data)
    return json.dumps(sorted_data, separators=(',', ':'))

def generate_hmac(data: dict):
    secret = current_app.config['SECRET_KEY']

    message = stable_json(data).encode()

    return hmac.new(
        secret.encode(),
        message,
        hashlib.sha256
    ).hexdigest()


def verify_hmac(data: dict, received_hmac: str):
    secret = current_app.config['SECRET_KEY']

    stable_string = stable_json(data)

    computed_hmac = hmac.new(
        secret.encode(),
        stable_string.encode(),
        hashlib.sha256
    ).hexdigest()

    print("\n===== DEBUG HMAC =====")
    print("DATA:", data)
    print("STRING:", stable_string)
    print("SIGNATURE RECEIVED:", received_hmac)
    print("SIGNATURE COMPUTED:", computed_hmac)
    print("======================\n")

    return hmac.compare_digest(computed_hmac, received_hmac)