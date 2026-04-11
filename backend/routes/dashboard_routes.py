from flask import Blueprint, jsonify
from models.log_model import Log
from models.fingerprint_model import Fingerprint

dash_bp = Blueprint('dashboard', __name__)

@dash_bp.route('/logs', methods=['GET'])
def get_logs():
    logs = Log.query.order_by(Log.id.desc()).all()
    data = []
    for log in logs:
        data.append({
            "id"       : log.id,
            "user_id"  : log.user_id,
            "action"   : log.action,
            "risk"     : log.risk,
            "breakdown": log.get_breakdown(),
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else ""
        })
    return jsonify(data)


@dash_bp.route('/logs/<int:log_id>', methods=['GET'])
def get_log_detail(log_id):
    log = Log.query.get_or_404(log_id)

    fp = Fingerprint.query.filter_by(user_id=log.user_id)\
        .order_by(Fingerprint.id.desc())\
        .first()

    fingerprint_data = None
    if fp:
        fingerprint_data = {
            "screen"          : fp.screen,
            "platform"        : fp.platform,
            "language"        : fp.language,
            "timezone"        : fp.timezone,
            "user_agent"      : fp.user_agent,
            "color_depth"     : fp.color_depth,
            "cores"           : fp.cores,
            "memory"          : fp.memory,
            "touch_points"    : fp.touch_points,
            "cookies_enabled" : fp.cookies_enabled,
            "trusted"         : fp.trusted,
            "fingerprint_hash": fp.fingerprint
        }

    reasons = []
    action = log.action or ''
    if 'New Device' in action:  reasons.append("🆕 New Device detected")
    if 'ML Anomaly' in action:  reasons.append("🤖 ML anomaly flagged")
    if 'High Risk' in action:   reasons.append("⚠️ Risk score exceeded threshold")
    if 'BLOCK' in action:       reasons.append("❌ Access blocked by policy")
    if 'OTP' in action:         reasons.append("⚡ Step-up OTP authentication triggered")
    if 'ALLOW' in action:       reasons.append("✅ Access granted by policy")
    if 'ALERT' in action:       reasons.append("🚨 Security alert raised")

    return jsonify({
        "id"            : log.id,
        "user_id"       : log.user_id,
        "action"        : log.action,
        "risk"          : log.risk,
        "breakdown"     : log.get_breakdown(),
        "timestamp"     : log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "",
        "reasons"       : reasons,
        "fingerprint"   : fingerprint_data
    })