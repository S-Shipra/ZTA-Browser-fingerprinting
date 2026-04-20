from utils.hmac_utils import verify_hmac
from utils.crypto_utils import encrypt_data, decrypt_data
from utils.jwt_utils import generate_token
import pyotp
import time

from flask import Blueprint, request, jsonify

from services.auth_service import authenticate_user
from services.fingerprint_service import generate_fingerprint
from services.risk_engine import calculate_risk
from services.policy_engine import decide_action
from services.monitoring_service import log_event
from services.ml_engine import is_outlier

from models.fingerprint_model import Fingerprint
from database.db import db
from models.user_model import User

from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)


# 🔐 LOGIN ROUTE
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    # 🔴 STEP 0: HMAC + REPLAY ATTACK PROTECTION
    timestamp = data.get("timestamp")

    if not timestamp or abs(time.time()*1000 - timestamp) > 5000:
        return jsonify({"message": "Request expired"}), 400

    payload = {
        "fingerprint": data['fingerprint'],
        "timestamp": timestamp
    }

    if not verify_hmac(payload, data.get("signature", "")):
        return jsonify({"message": "Invalid request signature"}), 400


    # 🔹 Step 1: Authenticate user
    user = authenticate_user(data['username'], data['password'])
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401


    # 🔹 Step 2: Generate fingerprint hash
    fingerprint_hash = generate_fingerprint(data['fingerprint'])


    # 🔹 Step 3: Check if device exists
    fp_record = Fingerprint.query.filter_by(
        user_id=user.id,
        fingerprint=fingerprint_hash
    ).first()

    risk = 0


    # 🔹 Step 4: Trusted device logic
    if not fp_record:
        risk += 50
    else:
        if not fp_record.trusted:
            risk += 20


    # 🔹 Step 5: Additional risk checks
    risk_data = calculate_risk(user, data['fingerprint'])
    base_risk = risk_data["total_risk"]
    risk += min(base_risk, 30)

    risk_breakdown = risk_data["breakdown"]
    if not fp_record:
        risk_breakdown["new_device"] = 50
    elif not fp_record.trusted:
        risk_breakdown["untrusted_device"] = 20


    # 🔹 Step 6: ML Outlier Detection
    fp_vector = [
        int(data['fingerprint']['screen'].split('x')[0]),
        int(data['fingerprint']['screen'].split('x')[1])
    ]

    ml_flag = False
    try:
        if is_outlier(fp_vector):
            risk += 10
            ml_flag = True
            risk_breakdown["ml_anomaly"] = 10
    except:
        pass


    # 🔹 Step 7: Decide action
    decision = decide_action(risk)


    # 🔴 ALERT SYSTEM
    alert = False
    if risk > 70:
        alert = True
        print("🚨 ALERT: Suspicious login detected!")


    # 🔹 Step 8: Save fingerprint if new and not blocked
    if not fp_record:
        if decision != "BLOCK":
            fp_data = data['fingerprint']
            new_fp = Fingerprint(
                user_id         = user.id,
                fingerprint     = fingerprint_hash,
                trusted         = False,
                screen          = fp_data.get('screen'),
                platform        = fp_data.get('platform'),
                language        = fp_data.get('language'),
                timezone        = fp_data.get('timezone'),
                user_agent      = fp_data.get('userAgent'),
                color_depth     = fp_data.get('colorDepth'),
                cores           = fp_data.get('cores'),
                memory          = str(fp_data.get('memory', 'unknown')),
                touch_points    = fp_data.get('touchPoints'),
                cookies_enabled = fp_data.get('cookiesEnabled'),
                canvas          = fp_data.get('canvas')
            )
            db.session.add(new_fp)


    # 🔹 Step 9: TOTP (REPLACED OLD OTP SYSTEM)
    otp_value = None

    if decision == "OTP":
        totp = pyotp.TOTP(user.otp_secret)
        otp_value = totp.now()

        print(f"🔐 TOTP for user {user.id}: {otp_value}")


    # 🔹 Step 10: JWT TOKEN
    token = generate_token(user.id, user.role)


    # 🔹 Step 11: Logging
    action = decision
    if alert:
        action = "ALERT_" + decision

    reasons = []
    if not fp_record: reasons.append("New Device")
    if ml_flag: reasons.append("ML Anomaly")
    if alert: reasons.append("High Risk")

    final_action = action
    if reasons:
        final_action = f"{action} | {', '.join(reasons)}"

    log_event(user.id, final_action, risk, breakdown=risk_breakdown)


    db.session.commit()


    # 🔹 FINAL RESPONSE (UPDATED)
    return jsonify({
        "decision": decision,
        "risk": risk,
        "token": token,
        "otp_required": decision == "OTP",
        "user_id": user.id
    })


# 🔐 OTP VERIFY (TOTP VERSION)
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json

    user_id = data['user_id']
    otp_input = data['otp']

    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    totp = pyotp.TOTP(user.otp_secret)

    if not totp.verify(otp_input):
        return jsonify({"message": "Invalid OTP"}), 400


    # 🔹 Mark latest device as trusted
    fp = Fingerprint.query.filter_by(user_id=user_id)\
        .order_by(Fingerprint.id.desc())\
        .first()

    if fp:
        fp.trusted = True

    db.session.commit()

    return jsonify({
        "message": "OTP Verified",
        "status": "ALLOW"
    })