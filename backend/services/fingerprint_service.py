import hashlib

def generate_fingerprint(data):
    # only hash stable attributes, not canvas (too volatile)
    stable = {
        "screen"        : data.get("screen"),
        "platform"      : data.get("platform"),
        "language"      : data.get("language"),
        "timezone"      : data.get("timezone"),
        "colorDepth"    : data.get("colorDepth"),
        "cores"         : data.get("cores"),
        "touchPoints"   : data.get("touchPoints"),
    }
    return hashlib.sha256(str(stable).encode()).hexdigest()