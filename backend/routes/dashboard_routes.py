from flask import Blueprint, jsonify
from models.log_model import Log

dash_bp = Blueprint('dashboard', __name__)

@dash_bp.route('/logs', methods=['GET'])
def get_logs():
    logs = Log.query.all()

    data = []

    for log in logs:
        data.append({
            "user_id": log.user_id,
            "action": log.action,
            "risk": log.risk,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else ""
        })

    return jsonify(data)