import os
from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WriteOptions
from modules.chronotrace_normalizer import ChronoTraceNormalizer

app = Flask(__name__)

# -----------------------------------------------------
# InfluxDB Client 初期化
# -----------------------------------------------------
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=WriteOptions(batch_size=1))

# -----------------------------------------------------
# Normalizer 初期化
# -----------------------------------------------------
normalizer = ChronoTraceNormalizer()

# -----------------------------------------------------
# /ingest エンドポイント
# -----------------------------------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    """
    期待される入力フォーマット:
    {
        "measurement": "ultralight_trace",
        "tags": {...},
        "fields": {...},
        "timestamp": "2025-11-14T05:12:00"
    }
    """
    raw = request.json

    if not raw:
        return jsonify({"status": "error", "reason": "no JSON payload"}), 400

    try:
        # 1. ChronoTrace 正規化
        normalized = normalizer.normalize_payload(raw)

        # 2. InfluxDB line protocol に変換
        point = (
            Point(normalized["measurement"])
            .time(normalized["timestamp"])
        )

        # tags
        for k, v in normalized["tags"].items():
            point = point.tag(k, v)

        # fields
        for k, v in normalized["fields"].items():
            point = point.field(k, v)

        # 3. 書き込み
        write_api.write(bucket=INFLUX_BUCKET, record=point)

        return jsonify({
            "status": "ok",
            "normalized": normalized
        })

    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


@app.route("/")
def root():
    return "ChronoNeura Ingest Server is running."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

# ============================
#  POST /ingest
# ============================
@app.route("/ingest", methods=["POST"])
def ingest():
    try:
        data = request.json

        measurement = data.get("measurement", "unknown")
        tags = data.get("tags", {})
        fields = data.get("fields", {})
        timestamp = data.get("timestamp", None)

        point = Point(measurement)

        for k, v in tags.items():
            point.tag(k, str(v))

        for k, v in fields.items():
            try:
                v = float(v)
                point.field(k, v)
            except:
                point.field(k, str(v))

        if timestamp:
            point.time(timestamp, WritePrecision.NS)

        write_api.write(bucket=INFLUX_BUCKET, record=point)

        return jsonify({"status": "success", "written": data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================
#  GET /last?measurement=X
# ============================
@app.route("/last", methods=["GET"])
def last_record():
    try:
        measurement = request.args.get("measurement", "ingest_test")

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


# ============================
#  Index
# ============================
@app.route("/")
def index():
    return "ChronoNeura Ingest Server — Fly.io OK"


# ============================
#  Run App
# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
