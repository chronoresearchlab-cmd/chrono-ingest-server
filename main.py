import os
from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions
from modules.chronotrace_normalizer import ChronoTraceNormalizer

# -----------------------------------------------------
# Flask App
# -----------------------------------------------------
app = Flask(__name__)

# -----------------------------------------------------
# InfluxDB Client 初期化
# -----------------------------------------------------
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")   # ← sandboxなら chrono_test を設定

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=WriteOptions(batch_size=1))
query_api = client.query_api()

# -----------------------------------------------------
# Normalizer 初期化
# -----------------------------------------------------
normalizer = ChronoTraceNormalizer()

# -----------------------------------------------------
#  POST /ingest（Normalizer 版）
# -----------------------------------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    """
    JSON例:
    {
      "measurement": "ultralight_trace",
      "tags": {...},
      "fields": {...},
      "timestamp": "2025-11-14T05:12:00Z"
    }
    """
    raw = request.json

    if not raw:
        return jsonify({"status": "error", "reason": "no JSON payload"}), 400

    try:
        # 正規化
        normalized = normalizer.normalize_payload(raw)

        # Influx Point 作成
        point = (
            Point(normalized["measurement"])
            .time(normalized["timestamp"], WritePrecision.NS)
        )

        # tags
        for k, v in normalized["tags"].items():
            point = point.tag(k, v)

        # fields
        for k, v in normalized["fields"].items():
            point = point.field(k, v)

        # 書き込み
        write_api.write(bucket=INFLUX_BUCKET, record=point)

        return jsonify({
            "status": "ok",
            "bucket": INFLUX_BUCKET,
            "normalized": normalized
        })

    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


# -----------------------------------------------------
#  GET /last?measurement=xxx
# -----------------------------------------------------
@app.route("/last", methods=["GET"])
def last_record():
    try:
        measurement = request.args.get("measurement", None)
        if not measurement:
            return jsonify({"status": "error", "reason": "measurement required"}), 400

        query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -30d)
          |> filter(fn: (r) => r._measurement == "{measurement}")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: 1)
        '''

        tables = query_api.query(query)

        results = []
        for table in tables:
            for record in table.records:
                results.append({
                    "time": str(record.get_time()),
                    "field": record.get_field(),
                    "value": record.get_value(),
                    "tags": record.values
                })

        return jsonify({"status": "success", "data": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -----------------------------------------------------
#  Index
# -----------------------------------------------------
@app.route("/")
def index():
    return f"ChronoNeura Ingest Server — OK (bucket={INFLUX_BUCKET})"


# -----------------------------------------------------
#  Run App
# -----------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
