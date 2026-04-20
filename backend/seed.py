import sys
import os
import pyotp

# ── Make sure `backend/` is on the path so `app`, `database`, `models` resolve
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Point SQLite at the correct absolute path BEFORE importing app
DB_PATH = os.path.join(BASE_DIR, "instance", "db.sqlite3")
os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"

from app import app
from database.db import db
from models.user_model import User
from models.log_model import Log
from models.fingerprint_model import Fingerprint
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone, timedelta
import json
import random

# ─────────────────────────────────────────────
#  DEMO DATA
# ─────────────────────────────────────────────

DEMO_USERS = [
    {"username": "admin",   "password": "admin123"},
    {"username": "user1",   "password": "user123"},
    {"username": "alice",   "password": "alice123"},
    {"username": "bob",     "password": "bob123"},
    {"username": "charlie", "password": "charlie123"},
]

DEMO_FINGERPRINTS = [
    {
        "screen": "1920x1080", "platform": "Win32",
        "language": "en-US",   "timezone": "America/New_York",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "color_depth": 24, "cores": 8, "memory": "8",
        "touch_points": 0, "cookies_enabled": True,
        "canvas": "canvas_win_chrome_120",
        "fingerprint": "aabbcc1234567890aabbcc1234567890aabbcc1234567890aabbcc1234567890",
    },
    {
        "screen": "375x812",  "platform": "iPhone",
        "language": "en-GB",  "timezone": "Europe/London",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1",
        "color_depth": 32, "cores": 6, "memory": "4",
        "touch_points": 5, "cookies_enabled": True,
        "canvas": "canvas_iphone_safari_16",
        "fingerprint": "ddeeff1234567890ddeeff1234567890ddeeff1234567890ddeeff1234567890",
    },
    {
        "screen": "1280x800", "platform": "MacIntel",
        "language": "en-US",  "timezone": "America/Los_Angeles",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "color_depth": 30, "cores": 10, "memory": "16",
        "touch_points": 0, "cookies_enabled": True,
        "canvas": "canvas_mac_chrome_119",
        "fingerprint": "112233445566778899001122334455667788990011223344556677889900aabb",
    },
    {
        "screen": "1366x768", "platform": "Linux x86_64",
        "language": "fr-FR",  "timezone": "Europe/Paris",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
        "color_depth": 24, "cores": 4, "memory": "4",
        "touch_points": 0, "cookies_enabled": False,
        "canvas": "canvas_linux_firefox_118",
        "fingerprint": "aabbccddeeff00112233aabbccddeeff00112233aabbccddeeff00112233aabb",
    },
    {
        "screen": "2560x1440", "platform": "Win32",
        "language": "de-DE",   "timezone": "Europe/Berlin",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edg/120.0.0.0 Safari/537.36",
        "color_depth": 32, "cores": 16, "memory": "32",
        "touch_points": 0, "cookies_enabled": True,
        "canvas": "canvas_win_edge_120",
        "fingerprint": "ffeeddccbbaa0099887766ffeeddccbbaa0099887766ffeeddccbbaa00998877",
    },
    {
        "screen": "412x915",  "platform": "Android",
        "language": "hi-IN",  "timezone": "Asia/Kolkata",
        "user_agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/118.0.0.0 Mobile Safari/537.36",
        "color_depth": 24, "cores": 8, "memory": "8",
        "touch_points": 10, "cookies_enabled": True,
        "canvas": "canvas_android_chrome_118",
        "fingerprint": "99887766554433221100998877665544332211009988776655443322110099aa",
    },
]

# (action, risk, breakdown, trusted_device)
DEMO_SCENARIOS = [
    ("ALLOW",                                        5,  {},                                                                       True),
    ("ALLOW",                                       10,  {"behaviour_score": 10},                                                  True),
    ("ALLOW",                                       20,  {"untrusted_device": 20},                                                 True),
    ("ALLOW",                                       25,  {"untrusted_device": 20, "behaviour_score": 5},                          True),
    ("OTP | New Device",                            55,  {"new_device": 50, "behaviour_score": 5},                                 False),
    ("OTP | New Device",                            60,  {"new_device": 50, "behaviour_score": 10},                                False),
    ("OTP | New Device",                            65,  {"new_device": 50, "behaviour_score": 15},                                False),
    ("ALERT_OTP | New Device, High Risk",           75,  {"new_device": 50, "behaviour_score": 25},                               False),
    ("BLOCK | New Device, High Risk",               80,  {"new_device": 50, "behaviour_score": 30},                               False),
    ("BLOCK | New Device, High Risk, ML Anomaly",   90,  {"new_device": 50, "behaviour_score": 30, "ml_anomaly": 10},             False),
    ("ALERT_BLOCK | High Risk",                    100,  {"new_device": 50, "behaviour_score": 30, "ml_anomaly": 10, "untrusted_device": 10}, False),
]

# ─────────────────────────────────────────────
#  SEED
# ─────────────────────────────────────────────

def run_demo_seed():
    with app.app_context():

        # Force the app to use our explicit DB path if it hasn't been set already
        if "sqlite" in app.config.get("SQLALCHEMY_DATABASE_URI", ""):
            # Check if it's a relative path and patch it
            uri = app.config["SQLALCHEMY_DATABASE_URI"]
            if "instance/db.sqlite3" in uri and not uri.startswith(f"sqlite:///{BASE_DIR}"):
                app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"

        print(f"📂 Using DB: {app.config.get('SQLALCHEMY_DATABASE_URI', 'unknown')}")

        # ── Drop & recreate so we always start clean ──
        db.drop_all()
        db.create_all()
        print("🗑️  Old data cleared — fresh tables created")

        # ── Users ──────────────────────────────────────
        users = []
        for u in DEMO_USERS:
            user = User(
                username=u["username"],
                password=generate_password_hash(u["password"]),
                otp_secret=pyotp.random_base32()
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()
        # Re-query so IDs are populated
        users = User.query.all()
        print(f"✅ {len(users)} users created")

        # ── Fingerprints (2 per user) ──────────────────
        fp_count = 0
        for i, user in enumerate(users):
            for j in range(2):
                fp_data = DEMO_FINGERPRINTS[(i * 2 + j) % len(DEMO_FINGERPRINTS)]
                fp = Fingerprint(
                    user_id         = user.id,
                    fingerprint     = fp_data["fingerprint"] + str(user.id) + str(j),  # unique per user
                    trusted         = (j == 0),   # first device trusted, second untrusted
                    screen          = fp_data["screen"],
                    platform        = fp_data["platform"],
                    language        = fp_data["language"],
                    timezone        = fp_data["timezone"],
                    user_agent      = fp_data["user_agent"],
                    color_depth     = fp_data["color_depth"],
                    cores           = fp_data["cores"],
                    memory          = fp_data["memory"],
                    touch_points    = fp_data["touch_points"],
                    cookies_enabled = fp_data["cookies_enabled"],
                    canvas          = fp_data["canvas"],
                )
                db.session.add(fp)
                fp_count += 1

        db.session.commit()
        print(f"✅ {fp_count} fingerprints created (2 per user)")

        # ── Logs (60 total, spread across past 7 days) ─
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        random.seed(42)   # reproducible

        for i in range(60):
            user     = users[i % len(users)]          # distribute evenly across users
            scenario = DEMO_SCENARIOS[i % len(DEMO_SCENARIOS)]   # cycle through scenarios
            # add a little randomness on top of the even distribution
            if i % 3 == 0:
                user     = random.choice(users)
                scenario = random.choice(DEMO_SCENARIOS)

            action, risk, breakdown, _ = scenario

            log = Log(
                user_id   = user.id,
                action    = action,
                risk      = risk,
                timestamp = base_time + timedelta(
                    hours   = random.randint(0, 167),
                    minutes = random.randint(0, 59),
                    seconds = random.randint(0, 59),
                ),
                breakdown = json.dumps(breakdown),
            )
            db.session.add(log)

        db.session.commit()
        print("✅ 60 demo logs created")

        # ── Summary ────────────────────────────────────
        print()
        print("=" * 40)
        print("  DEMO SEED COMPLETE")
        print("=" * 40)
        print(f"  Users:        {User.query.count()}")
        print(f"  Fingerprints: {Fingerprint.query.count()}")
        print(f"  Logs:         {Log.query.count()}")
        print()
        print("  Login credentials:")
        print("    admin    / admin123")
        print("    user1    / user123")
        print("    alice    / alice123")
        print("    bob      / bob123")
        print("    charlie  / charlie123")
        print("=" * 40)


if __name__ == "__main__":
    try:
        run_demo_seed()
    except Exception as e:
        print(f"\n❌ Seed failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)