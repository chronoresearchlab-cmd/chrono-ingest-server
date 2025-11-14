# routes/ingest_api.py
# ChronoNeura Ingest API v1

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 正しい import（modules 配下）
from utils.influx_client import influx_write_point
from modules.bucket_selector import bucket_selector
from modules.chronotrace_normalizer import ChronoTraceNormalizer

router = APIRouter()
normalizer = ChronoTraceNormalizer()


# --------------------------
# 入力モデル
# --------------------------
class IngestPayload(BaseModel):
    bucket: str | None = None
    mode: str | None = None   # "sandbox" or "prod"
    measurement: str
    fields: dict
    tags: dict | None = None
    timestamp: str | None = None


# --------------------------
# Ingest API
# --------------------------
@router.post("/ingest")
async def ingest(payload: IngestPayload):

    # bucket を決定（sandbox / prod）
    selected_bucket = bucket_selector(payload.mode, payload.bucket)

    # キーの正規化
    measurement = normalizer.normalize_key(payload.measurement)
    fields = normalizer.normalize_fields(payload.fields)
    tags = {normalizer.normalize_key(k): normalizer.normalize_value(v)
            for k, v in (payload.tags or {}).items()}

    try:
        result = influx_write_point(
            bucket=selected_bucket,
            measurement=measurement,
            fields=fields,
            tags=tags,
            timestamp=payload.timestamp,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {e}")

    return {
        "status": "ok",
        "bucket": selected_bucket,
        "normalized": {
            "measurement": measurement,
            "fields": fields,
            "tags": tags,
            "timestamp": payload.timestamp,
        },
    }
