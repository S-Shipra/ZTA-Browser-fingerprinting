from database.db import db
from datetime import datetime, timezone

class Fingerprint(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer)
    fingerprint       = db.Column(db.String(256))
    trusted           = db.Column(db.Boolean, default=False)
    first_seen        = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Basic
    screen            = db.Column(db.String(50))
    platform          = db.Column(db.String(50))
    language          = db.Column(db.String(20))
    
    # New
    timezone          = db.Column(db.String(100))
    user_agent        = db.Column(db.String(300))
    color_depth       = db.Column(db.Integer)
    cores             = db.Column(db.Integer)
    memory            = db.Column(db.String(20))
    touch_points      = db.Column(db.Integer)
    cookies_enabled   = db.Column(db.Boolean)
    canvas            = db.Column(db.Text)