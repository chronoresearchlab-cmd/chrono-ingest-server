import os
from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions
from modules.chronotrace_normalizer import ChronoTraceNormalizer

app = Flask(__name__)

# -----------------------------------------------------
# InfluxDB base settings (共通)
# -----------------------------------------------------
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")

# バケット切り替え用
BUCKETS = {
    "prod": os.getenv("INFLUX_BUCKET"),        # 本番
    "sandbox": os.getenv("INFLUX_BUCKET_SB"),  # sandbox モード
}

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=WriteOptions(batch_size=1))
query_api = client.query_api()

# Normalizer
normalizer = ChronoTraceNormalizer()


# -----------------------------------------------------
# POST /ingest
# -----------------------------------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    raw = request.json
    if not raw:
        return jsonify({"status": "error", "reason": "no JSON payload"}), 400

    try:
        # -----------------------------
        # ① mode 判定
        # -----------------------------
        mode = request.args.get("mode", raw.get("mode", "prod"))
        bucket = BUCKETS.get(mode, BUCKETS["prod"])

        # -----------------------------
        # ② ChronoTrace 正規化
        # -----------------------------
        # after
        normalized = normalizer.normalize_dict(raw)

        # -----------------------------
        # ③ Influx Point 生成
        # -----------------------------
        point = (
            Point(normalized["measurement"])
            .time(normalized["timestamp"], WritePrecision.NS)
        )

        for k, v in normalized["tags"].items():
            point = point.tag(k, v)

        for k, v in normalized["fields"].items():
            point = point.field(k, v)

        # -----------------------------
        # ④ 書き込み (← modeによる bucket 切り替え)
        # -----------------------------
        write_api.write(bucket=bucket, record=point)

        return jsonify({
            "status": "ok",
            "mode": mode,
            "bucket": bucket,
            "normalized": normalized
        })

    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


# -----------------------------------------------------
# GET /last?measurement=xxx&mode=sandbox
# -----------------------------------------------------
@app.route("/last", methods=["GET"])
def last_record():
    try:
        measurement = request.args.get("measurement")
        if not measurement:
            return jsonify({"status": "error", "reason": "measurement required"}), 400

        mode = request.args.get("mode", "prod")
        bucket = BUCKETS.get(mode, BUCKETS["prod"])

        query = f'''
        from(bucket: "{bucket}")
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

        return jsonify({
            "status": "success",
            "mode": mode,
            "bucket": bucket,
            "data": results
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -----------------------------------------------------
# index
# -----------------------------------------------------
@app.route("/")
def index():
    return "ChronoNeura Ingest Server — mode-switch enabled"


# -----------------------------------------------------
# main
# -----------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
