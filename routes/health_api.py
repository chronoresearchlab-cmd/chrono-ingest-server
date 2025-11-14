# routes/health_api.py
from flask import Blueprint, jsonify
from utils.influx_client import influx_client
import datetime

health_bp = Blueprint("health_api", __name__)


# ================================
# 1. /health → アプリの生存確認
# ================================
@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "ChronoNeura Ingest Server",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })


# ================================
# 2. /health/influx → Influx 接続確認
# ================================
@health_bp.route("/health/influx", methods=["GET"])
def health_influx():
    """
    InfluxDB へクエリが通るか最低限チェック。
    """
    try:
        influx_client.ping()
        return jsonify({
            "status": "ok",
            "influx": "reachable"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "influx": "unreachable",
            "reason": str(e)
        }), 500


# ================================
# 3. /health/ready → ingestion-ready 状態
# ================================
@health_bp.route("/health/ready", methods=["GET"])
def health_ready():
    """
    ingestion が準備完了かチェック。
    用途: Fly.io のヘルスチェック, Notion Auto-Journal, SyncBridge
    """
    try:
        influx_client.ping()
        return jsonify({
            "status": "ready",
            "components": {
                "flask": "ok",
                "influx": "ok",
                "ingest": "ready"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "not_ready",
            "components": {
                "flask": "ok",
                "influx": "fail",
                "ingest": "blocked"
            },
            "reason": str(e)
        }), 503
