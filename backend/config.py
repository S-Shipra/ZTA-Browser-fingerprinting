import os

class Config:
    SECRET_KEY = "secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False