from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.notion_client import NotionWriter

app = FastAPI(
    title="ChronoNeura Ingest Server",
    description="SyncBridge → NotionWriter Ingest",
    version="1.0.0"
)

# -------- Input data model --------
class NotionIngestModel(BaseModel):
    mode: str = "create"    # create / upsert / append
    key: str | None = None
    title: str | None = None
    summary: str | None = None
    details: str | None = None
    category: list[str] | None = None
    append: str | None = None


# -------- API route --------
@app.post("/notion/devlog")
def ingest_devlog(data: NotionIngestModel):
    """
    NotionWriter.write_dynamic() に入力するための
    ingest endpoint
    """
    try:
        writer = NotionWriter()
        res = writer.write_dynamic(data.dict())
        return {
            "status": "success",
            "page_id": res.get("id"),
            "url": res.get("url")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- health --------
@app.get("/health")
def health():
    return {"status": "ok"}
