from datetime import datetime
from models.fingerprint_model import Fingerprint


# 🔷 Get last stored fingerprint (latest device)
def get_last_fingerprint(user_id):
    fp = Fingerprint.query.filter_by(user_id=user_id)\
        .order_by(Fingerprint.id.desc())\
        .first()

    return fp


# 🔷 Check unusual login time
def unusual_login_time():
    hour = datetime.now().hour
    return hour < 6 or hour > 23


# 🔷 MAIN RISK FUNCTION (UPGRADED)
def calculate_risk(user, new_fp_data):

    risk = 0
    breakdown = {}

    last_fp = get_last_fingerprint(user.id)

    if not last_fp:
        return {
            "total_risk": 50,
            "breakdown": {
                "new_device": 50
            }
        }

    # 🔹 Screen
    if new_fp_data.get('screen') != last_fp.screen:
        breakdown["screen_mismatch"] = 40
        risk += 40

    # 🔹 Platform
    if new_fp_data.get('platform') != last_fp.platform:
        breakdown["platform_mismatch"] = 30
        risk += 30

    # 🔹 Language
    if new_fp_data.get('language') != last_fp.language:
        breakdown["language_mismatch"] = 5
        risk += 5

    # 🔹 Time anomaly
    if unusual_login_time():
        breakdown["time_anomaly"] = 20
        risk += 20

    return {
        "total_risk": risk,
        "breakdown": breakdown
    }

    