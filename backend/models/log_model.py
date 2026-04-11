from database.db import db
from datetime import datetime, timezone
import json

class Log(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer)
    action     = db.Column(db.String(50))
    risk       = db.Column(db.Integer)
    timestamp  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    breakdown  = db.Column(db.Text)  # stored as JSON string

    def get_breakdown(self):
        try:
            return json.loads(self.breakdown) if self.breakdown else {}
        except:
            return {}