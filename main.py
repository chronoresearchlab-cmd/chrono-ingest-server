# main.py
# ChronoNeura Ingest Server - FastAPI entrypoint

from fastapi import FastAPI

from routes.ingest_api import router as ingest_router
from routes.query_api import router as query_router

app = FastAPI(
    title="ChronoNeura Ingest Server",
    version="1.0.0",
)

# ----------------------------
# ベーシックな疎通確認エンドポイント
# ----------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "ChronoNeura Ingest Server — mode-switch enabled",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ----------------------------
# ルーター登録
# ----------------------------

# 例:
#   POST /ingest/sandbox
#   POST /ingest/prod
app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])

# 例:
#   GET /query/ping
app.include_router(query_router, prefix="/query", tags=["query"])
