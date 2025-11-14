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


# ------------------------------------------
# 🔽 ここ！ ここに追加する！（重要）
# ------------------------------------------

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

        tables = client.query_api().query(query, org=INFLUX_ORG)

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


# ------------------------------------------
# ここから index() が続く
# ------------------------------------------

@app.route("/")
def index():
    return "ChronoNeura Ingest Server — Running on Fly.io"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
