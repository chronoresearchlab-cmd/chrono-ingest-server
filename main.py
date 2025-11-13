from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WriteOptions
import os

app = Flask(__name__)

# -----------------------------------------
# InfluxDB 設定
# -----------------------------------------
INFLUX_URL = os.getenv("INFLUX_URL", "")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "")
INFLUX_ORG = os.getenv("INFLUX_ORG", "")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "chrononeura")

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=WriteOptions(batch_size=1))

# -----------------------------------------
# /ingest API
# -----------------------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON provided"}), 400

        measurement = data.get("measurement", "chronotrace")
        fields = data.get("fields", {})
        tags = data.get("tags", {})
        timestamp = data.get("timestamp", None)

        point = Point(measurement)

        for k, v in tags.items():
            point = point.tag(k, v)

        for k, v in fields.items():
            point = point.field(k, v)

        if timestamp:
            point = point.time(timestamp)

        write_api.write(bucket=INFLUX_BUCKET, record=point)
        return jsonify({"status": "success", "written": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -----------------------------------------
# Root
# -----------------------------------------
@app.route("/")
def root():
    return "ChronoNeura Ingest API is running.\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
