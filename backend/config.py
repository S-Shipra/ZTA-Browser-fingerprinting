import os

class Config:

    # Use environment variables (secure)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")

    # Fernet key must be set in env
    FERNET_KEY = os.getenv("FERNET_KEY")

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "instance",
        "db.sqlite3"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False