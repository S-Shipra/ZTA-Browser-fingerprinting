from datetime import datetime
from models.fingerprint_model import Fingerprint
from services.attribute_weights import get_weight   # ← Shannon entropy weights


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


# 🔷 MAIN RISK FUNCTION (ENTROPY-WEIGHTED)
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

    # 🔹 Screen — uses Shannon entropy weight for Screen_Inner
    if new_fp_data.get('screen') != last_fp.screen:
        w = get_weight("Screen_Inner")
        breakdown["screen_mismatch"] = w
        risk += w

    # 🔹 Platform — uses Shannon entropy weight for Feature_OS
    if new_fp_data.get('platform') != last_fp.platform:
        w = get_weight("Feature_OS")
        breakdown["platform_mismatch"] = w
        risk += w

    # 🔹 Language — uses Shannon entropy weight for Language
    if new_fp_data.get('language') != last_fp.language:
        w = get_weight("Language")
        breakdown["language_mismatch"] = w
        risk += w

    # 🔹 Time anomaly (unchanged)
    if unusual_login_time():
        breakdown["time_anomaly"] = 20
        risk += 20

    return {
        "total_risk": risk,
        "breakdown": breakdown
    }