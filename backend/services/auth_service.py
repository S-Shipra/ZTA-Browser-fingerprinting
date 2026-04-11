from models.user_model import User
from utils.hash_utils import hash_password
from database.db import db

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()

    if user and user.password == hash_password(password):
        return user

    return None