# utils/notion_client.py

import os
import requests
from datetime import datetime

NOTION_TOKEN = os.getenv("NOTION_TOKEN_AUTOJOURNAL")
NOTION_API_URL = "https://api.notion.com/v1/pages"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def _wrap_value(value):
    """値の型に応じてNotionのproperty形式に変換"""
    
    if isinstance(value, str):
        # 文字列は title / rich_text どちらにも変換できるが、
        # ここでは rich_text を基本にする
        return {"rich_text": [{"text": {"content": value}}]}

    if isinstance(value, (int, float)):
        return {"number": value}

    if isinstance(value, datetime):
        return {"date": {"start": value.isoformat()}}

    # ISO8601 形式の文字列が来た場合、dateとして扱う
    try:
        parsed = datetime.fromisoformat(value)
        return {"date": {"start": parsed.isoformat()}}
    except:
        pass

    # fallback: rich_text
    return {"rich_text": [{"text": {"content": str(value)}}]}


def create_page(data: dict, database_id: str):
    """汎用 Notion ページ作成関数（DB構造に依存しない）"""

    if not NOTION_TOKEN:
        return {"error": "NOTION_TOKEN_AUTOJOURNAL が未設定"}

    properties = {}
    for key, value in data.items():
        properties[key] = _wrap_value(value)

    payload = {
        "parent": {"database_id": database_id},
        "properties": properties
    }

    r = requests.post(NOTION_API_URL, headers=HEADERS, json=payload)

    if r.status_code != 200:
        return {
            "status": r.status_code,
            "error": r.json()
        }

    return {
        "status": 200,
        "url": r.json().get("url")
    }
