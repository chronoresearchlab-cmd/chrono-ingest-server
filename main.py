from flask import Flask, request, jsonify
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision

app = Flask(__name__)

# ==== Fly.io Secrets ====
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

# ==== InfluxDB Client ====
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()

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
            # 数値として書き込み（文字列なら float に変換）
            try:
                v = float(v)
                point.field(k, v)
            except:
                point.field(k, str(v))

        if timestamp:
            point.time(timestamp, WritePrecision.NS)

        write_api.write(bucket=INFLUX_BUCKET, record=point)

        return jsonify({
            "status": "success",
            "written": data
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/")
def index():
    return "ChronoNeura Ingest Server — Running on Fly.io"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
