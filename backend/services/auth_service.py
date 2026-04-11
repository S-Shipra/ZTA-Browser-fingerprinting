from models.user_model import User
from werkzeug.security import check_password_hash

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        return user

    return None