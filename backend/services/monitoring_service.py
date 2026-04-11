from models.log_model import Log
from database.db import db
import json

def log_event(user_id, action, risk, breakdown=None):
    log = Log(
        user_id   = user_id,
        action    = action,
        risk      = risk,
        breakdown = json.dumps(breakdown) if breakdown else json.dumps({})
    )
    db.session.add(log)