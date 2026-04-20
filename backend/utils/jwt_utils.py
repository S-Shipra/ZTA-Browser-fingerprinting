import jwt
from flask import current_app
from datetime import datetime, timedelta

def generate_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")


def verify_token(token):
    return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])