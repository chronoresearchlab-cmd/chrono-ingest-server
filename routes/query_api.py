# routes/query_api.py

from fastapi import APIRouter, HTTPException
from utils.influx_client import influx_query
from modules.bucket_selector import bucket_selector

router = APIRouter()


@router.get("/query")
async def query_api(mode: str = "prod", bucket: str | None = None, q: str = ""):

    selected_bucket = bucket_selector(mode, bucket)

    try:
        results = influx_query(bucket=selected_bucket, query=q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

    return {
        "bucket": selected_bucket,
        "query": q,
        "results": results,
    }
