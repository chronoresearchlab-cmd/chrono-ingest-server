# utils/influx_client.py
import os
from influxdb_client import InfluxDBClient, WriteOptions

# ======================================================
# InfluxDB 設定（Fly.io Secret から取得）
# ======================================================
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")

# URL / TOKEN / ORG が未設定の場合は起動時に例外
if not (INFLUX_URL and INFLUX_TOKEN and INFLUX_ORG):
    raise Exception("InfluxDB 環境変数 (URL/TOKEN/ORG) が設定されていません。")


# ======================================================
# InfluxDB Client 生成（Singleton）
# ======================================================
influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG,
    timeout=30_000  # 30秒タイムアウト
)

# ======================================================
# Write / Query API（共通で使用）
# ======================================================
write_api = influx_client.write_api(
    write_options=WriteOptions(batch_size=1)  # 即時書き込み
)

query_api = influx_client.query_api()


# ======================================================
# 便利レイヤー：Ping / バケット存在チェック
# ======================================================
def check_connection():
    """
    InfluxDB ping 確認
    """
    try:
        influx_client.ping()
        return True
    except:
        return False


def bucket_exists(bucket_name: str) -> bool:
    """
    バケット存在確認（Sandbox / Prod 自動テストに使用）
    """
    try:
        buckets = influx_client.buckets_api().find_bucket_by_name(bucket_name)
        return buckets is not None
    except:
        return False


# ======================================================
# 書き込み（低レベル API を隠蔽）
# ======================================================
def write_point(bucket: str, point):
    """
    Fly.io routes から統一して使用できる write wrapper。
    """
    write_api.write(bucket=bucket, record=point)


# ======================================================
# Flux 実行（POST /query が利用）
# ======================================================
def run_flux(flux: str):
    """
    Flux クエリの実行をラップした関数。
    """
    return query_api.query(query=flux)
