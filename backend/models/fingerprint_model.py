from database.db import db

class Fingerprint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    fingerprint = db.Column(db.String(256))
    trusted = db.Column(db.Boolean, default=False)
    first_seen = db.Column(db.DateTime)
    screen = db.Column(db.String(50))
    platform = db.Column(db.String(50))
    language = db.Column(db.String(20))