from database.db import db
from datetime import datetime, timezone

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    otp = db.Column(db.String(6))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))