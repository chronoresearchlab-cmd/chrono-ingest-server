# routes/health_api.py
# ChronoNeura Health Check API (FastAPI版)

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}
