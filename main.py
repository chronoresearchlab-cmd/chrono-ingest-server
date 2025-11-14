# main.py
# ChronoNeura Ingest Server — Route-split version
#
# - /ingest  → データ投入
# - /query   → データ取得（Flux）
# - /health  → 生存確認
# - Mode-switch (sandbox / prod)
# - FastAPI router 統合
#

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routes
from routes.ingest_api import router as ingest_router
from routes.query_api import router as query_router
from routes.health_api import router as health_router


# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(
    title="ChronoNeura Ingest Server",
    description="ChronoNeura ingestion/query microservice",
    version="1.0.0"
)

# -------------------------------
# CORS（ChronoNeura Viewer / Notion / Local dev に対応）
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 必要ならドメインを絞る
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Routers
# -------------------------------
app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(query_router, prefix="/query", tags=["query"])
app.include_router(health_router, prefix="/health", tags=["health"])


# -------------------------------
# Root endpoint（ブラウザ確認用）
# -------------------------------
@app.get("/")
def index():
    return {
        "service": "ChronoNeura Ingest Server",
        "mode-switch": "enabled",
        "routes": {
            "/ingest": "データ投入",
            "/query": "クエリ実行",
            "/health": "動作確認",
        }
    }
