from models.log_model import Log
from database.db import db

def log_event(user_id, action, risk):
    log = Log(user_id=user_id, action=action, risk=risk)
    db.session.add(log)
    