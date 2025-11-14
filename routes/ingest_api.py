# routes/ingest_api.py
# ChronoNeura Ingest API v1
#
# - sandbox / prod の Mode で bucket を切り替えて書き込み
# - key 正規化は ChronoTraceNormalizer に集約
# - influx への write は influx_client.write_point()
#
# 依存：
#   utils/influx_client.py
#   utils/bucket_selector.py
#   utils/normalizer.py
#

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.influx_client import influx_client
from utils.bucket_selector import bucket_selector
from utils.normalizer import ChronoTraceNormalizer

router = APIRouter()
normalizer = ChronoTraceNormalizer()


# --------------------------
# Pydantic Input Model
# --------------------------
class IngestPayload(BaseModel):
    bucket: str | None = None
    mode: str | None = None               # "sandbox" / "prod"
    measurement: str
    tags: dict | None = None
    fields: dict
    timestamp: str | None = None          # ISO 8601


# --------------------------
# POST /ingest
# --------------------------
@router.post("/ingest")
async def ingest_data(payload: IngestPayload):
    """
    ChronoNeura ingestion endpoint.

    Steps:
      1. Select bucket (sandbox or prod)
      2. Normalize measurement / tags / fields
      3. Write to InfluxDB
    """

    try:
        # 1) bucket selection
        bucket = bucket_selector.select(payload.mode)

        # payload.bucket があればそちらを優先（上書き）
        if payload.bucket:
            bucket = payload.bucket

        # 2) normalization
        measurement = normalizer.normalize_key(payload.measurement)
        tags = normalizer.normalize_fields(payload.tags or {})
        fields = normalizer.normalize_fields(payload.fields)

        # 3) write to influx
        influx_client.write_point(
            bucket=bucket,
            measurement=measurement,
            tags=tags,
            fields=fields,
            timestamp=payload.timestamp
        )

        return {
            "status": "ok",
            "bucket": bucket,
            "normalized": {
                "measurement": measurement,
                "tags": tags,
                "fields": fields,
                "timestamp": payload.timestamp,
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingest failed: {str(e)}"
    )
