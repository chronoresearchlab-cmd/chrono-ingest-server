# routes/query_api.py
from flask import Blueprint, request, jsonify
from utils.influx_client import query_api
from modules.bucket_selector import select_bucket

query_bp = Blueprint("query_api", __name__)


# ================================
# 1. /last?measurement=xxx&mode=sandbox
# ================================
@query_bp.route("/last", methods=["GET"])
def last_record():
    """
    指定 measurement の最新1件を返す
    mode = prod / sandbox
    """
    measurement = request.args.get("measurement")
    if not measurement:
        return jsonify({"status": "error", "reason": "measurement required"}), 400

    mode = request.args.get("mode", "prod")
    bucket = select_bucket(mode)

    flux = f'''
    from(bucket: "{bucket}")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "{measurement}")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 1)
    '''

    try:
        tables = query_api.query(query=flux)
        results = []

        for table in tables:
            for record in table.records:
                results.append({
                    "time": str(record.get_time()),
                    "field": record.get_field(),
                    "value": record.get_value(),
                    "tags": record.values
                })

        return jsonify({"status": "ok", "bucket": bucket, "data": results})

    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500



# ================================
# 2. /query （任意 Flux クエリ実行）
# ================================
@query_bp.route("/query", methods=["POST"])
def raw_query():
    """
    {
        "mode": "sandbox",
        "flux": "from(bucket:\"chrono_test\") |> range(start:-1h)"
    }
    """
    body = request.json or {}
    mode = body.get("mode", "prod")
    flux = body.get("flux")

    if not flux:
        return jsonify({"status": "error", "reason": "flux script required"}), 400

    # bucket が flux 内で正しく参照されているかは利用者に委ねる
    try:
        tables = query_api.query(query=flux)
        results = []

        for table in tables:
            for record in table.records:
                results.append({
                    "time": str(record.get_time()),
                    "measurement": record.get_measurement(),
                    "field": record.get_field(),
                    "value": record.get_value(),
                    "tags": record.values
                })

        return jsonify({"status": "ok", "mode": mode, "data": results})

    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500
