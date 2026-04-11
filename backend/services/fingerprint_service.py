import hashlib

def generate_fingerprint(data):
    return hashlib.sha256(str(data).encode()).hexdigest()