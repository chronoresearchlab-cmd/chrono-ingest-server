# utils/influx_client.py
# ChronoNeura InfluxDB Client v1

import os
from influxdb_client import InfluxDBClient, Point, WriteOptions

INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")

# ------------------------------------
# InfluxDB クライアント生成
# ------------------------------------
client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG,
    timeout=10000,
)

write_api = client.write_api(write_options=WriteOptions(batch_size=1))
query_api = client.query_api()


# ------------------------------------
# 書き込みモジュール（正式名：influx_write_point）
# ------------------------------------
def influx_write_point(bucket: str, measurement: str, fields: dict, tags: dict, timestamp: str | None):
    try:
        p = Point(measurement)

        # tags
        for k, v in tags.items():
            p = p.tag(k, v)

        # fields
        for k, v in fields.items():
            p = p.field(k, v)

        # timestamp
        if timestamp:
            p = p.time(timestamp)

        write_api.write(bucket=bucket, record=p)
        return True

    except Exception as e:
        raise RuntimeError(f"Influx write failed: {e}")


# ------------------------------------
# クエリモジュール
# ------------------------------------
def influx_query(bucket: str, query: str):
    try:
        q = f'from(bucket:"{bucket}") |> {query}'
        tables = query_api.query(org=INFLUX_ORG, query=q)

        results = []
        for table in tables:
            for row in table.records:
                results.append(row.values)

        return results

    except Exception as e:
        raise RuntimeError(f"Influx query failed: {e}")
