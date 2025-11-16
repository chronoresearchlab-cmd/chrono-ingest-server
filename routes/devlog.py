from fastapi import APIRouter
from utils.notion_client import NotionClient
from datetime import datetime

router = APIRouter()
notion = NotionClient()

@router.post("/devlog/append")
async def append_devlog(payload: dict):
    """
    payload = {
        "Key": "20251116-Dev",
        "append_to": "Details",   # "Summary" or "NextAction" も可
        "text": "新しいログを追加します…",
    }
    """

    key = payload["Key"]
    append_to = payload.get("append_to", "Details")
    new_text = payload["text"]

    # 1. 既存ページ取得
    page = notion.find_page_by_key(notion.devlog_db, "Key", key)
    if not page:
        return {"status": "error", "message": "page not found", "key": key}

    page_id = page["id"]

    # 2. 既存 rich_text を抽出
    current_val = page["properties"].get(append_to)
    if current_val and "rich_text" in current_val:
        existing_text = "".join([rt["plain_text"] for rt in current_val["rich_text"]])
    else:
        existing_text = ""

    # 3. Append（2行以上の追記も自然に）
    if existing_text:
        updated_val = existing_text + "\n" + new_text
    else:
        updated_val = new_text

    # 4. Notion プロパティ更新
    props = {
        append_to: {
            "rich_text": [
                {"type": "text", "text": {"content": updated_val}}
            ]
        },
        "UpdatedAt": {"date": {"start": datetime.utcnow().isoformat()}}
    }

    notion.update_page(page_id, props)

    return {
        "status": "ok",
        "page_id": page_id,
        "append_to": append_to,
        "added_text": new_text
      }
