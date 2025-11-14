from flask import Blueprint, request, jsonify
from modules.chronotrace_normalizer import ChronoTraceNormalizer
from modules.bucket_selector import select_bucket
from utils.influx_client import write_api

ingest_bp = Blueprint("ingest_api", __name__)

normalizer = ChronoTraceNormalizer()

@ingest_bp.route("/ingest", methods=["POST"])
def ingest():
    raw = request.json or {}

    mode = request.args.get("mode", raw.get("mode", "prod"))
    bucket = select_bucket(mode)

    # 正規化
    normalized = normalizer.normalize_payload(raw)

    # InfluxDB point 化
    point = normalizer.to_point(normalized)

    write_api.write(bucket=bucket, record=point)

    return jsonify({
        "status": "ok",
        "bucket": bucket,
        "normalized": normalized
    })
