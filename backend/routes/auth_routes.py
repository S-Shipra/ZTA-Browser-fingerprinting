from flask import Blueprint, request, jsonify

from services.auth_service import authenticate_user
from services.fingerprint_service import generate_fingerprint
from services.risk_engine import calculate_risk
from services.policy_engine import decide_action
from services.monitoring_service import log_event
from services.ml_engine import is_outlier

from utils.otp_utils import generate_otp

from models.fingerprint_model import Fingerprint
from models.otp_model import OTP

from database.db import db

from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

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
        risk += 50   # New device
    else:
        if not fp_record.trusted:
            risk += 20   # Known but not trusted

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

    # 🔹 Step 9: OTP logic
    otp_value = None
    if decision == "OTP":
        otp_value = generate_otp()
        otp_entry = OTP(user_id=user.id, otp=otp_value)
        db.session.add(otp_entry)
        print(f"🔐 OTP for user {user.id}: {otp_value}")

    # 🔹 Step 10: Log event
    action = decision
    if alert:
        action = "ALERT_" + decision

    reasons = []
    if not fp_record:       reasons.append("New Device")
    if ml_flag:             reasons.append("ML Anomaly")
    if alert:               reasons.append("High Risk")

    final_action = action
    if reasons:
        final_action = f"{action} | {', '.join(reasons)}"

    log_event(user.id, final_action, risk, breakdown=risk_breakdown)
    db.session.commit()

    return jsonify({
        "decision"      : decision,
        "risk"          : risk,
        "risk_breakdown": risk_breakdown,
        "ml_detected"   : ml_flag,
        "otp_required"  : decision == "OTP",
        "alert"         : alert,
        "user_id"       : user.id
    })


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json

    user_id   = data['user_id']
    otp_input = data['otp']

    otp_record = OTP.query.filter_by(user_id=user_id, otp=otp_input).first()

    if not otp_record:
        return jsonify({"message": "Invalid OTP"}), 400

    fp = Fingerprint.query.filter_by(user_id=user_id)\
        .order_by(Fingerprint.id.desc())\
        .first()

    if fp:
        fp.trusted = True

    db.session.delete(otp_record)
    db.session.commit()

    return jsonify({"message": "OTP Verified", "status": "ALLOW"})