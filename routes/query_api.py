# routes/query_api.py
# ChronoNeura Query API v1
#
# - sandbox / prod の Mode で bucket を自動切替
# - influx_client.query() に集約
# - bucket_selector に完全準拠
#

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.influx_client import influx_client
from utils.bucket_selector import bucket_selector
from utils.normalizer import ChronoTraceNormalizer

router = APIRouter()
normalizer = ChronoTraceNormalizer()


# -------------------------------
# Pydantic Model
# -------------------------------
class QueryPayload(BaseModel):
    bucket: str | None = None
    mode: str | None = None       # "sandbox" / "prod"
    measurement: str | None = None
    limit: int | None = 100
    start: str | None = None      # RFC3339
    stop: str | None = None       # RFC3339
    raw_query: str | None = None  # 直接 Flux クエリを書く場合


# -------------------------------
# POST /query
# -------------------------------
@router.post("/query")
async def run_query(payload: QueryPayload):
    """
    ChronoNeura Query Endpoint.
    - bucket selector
    - key normalization for measurement
    - safe limit
    - raw Flux query override
    """

    try:
        # 1) bucket automatic selection
        bucket = bucket_selector.select(payload.mode)

        if payload.bucket:
            bucket = payload.bucket

        # 2) measurement normalization
        measurement = None
        if payload.measurement:
            measurement = normalizer.normalize_key(payload.measurement)

        # 3) raw query override
        if payload.raw_query:
            flux_query = payload.raw_query
        else:
            # Generate minimal Flux query
            if not measurement:
                raise HTTPException(
                    status_code=400,
                    detail="measurement または raw_query が必要です"
                )

            # Time range
            time_range = ""
            if payload.start and payload.stop:
                time_range = f'|> range(start: {payload.start}, stop: {payload.stop})'
            else:
                time_range = "|> range(start: -7d)"   # default 7 days

            flux_query = f'''
from(bucket: "{bucket}")
    {time_range}
    |> filter(fn: (r) => r["_measurement"] == "{measurement}")
    |> limit(n: {payload.limit})
'''

        # 4) Execute query
        rows = influx_client.query(flux_query)

        return {
            "status": "ok",
            "bucket": bucket,
            "measurement": measurement,
            "query": flux_query,
            "results": rows
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
            )
