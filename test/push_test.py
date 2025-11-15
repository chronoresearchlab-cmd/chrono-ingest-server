import os
import requests
from datetime import datetime

NOTION_TOKEN = os.environ.get("NOTION_TOKEN_AUTOJOURNAL")
DATABASE_ID = os.environ.get("NOTION_DB_AUTOJOURNAL_ID")

def create_notion_entry():
    """Auto-Journal 用最小書き込みテスト"""

    if not NOTION_TOKEN:
        print("ERROR: NOTION_TOKEN_AUTOJOURNAL が未設定です")
        return

    if not DATABASE_ID:
        print("ERROR: NOTION_DB_AUTOJOURNAL_ID が未設定です")
        return

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    now = datetime.now().isoformat()

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": f"Auto-Journal Test: {now}"}}
                ]
            },
            "Date": {
                "date": {"start": now}
            },
            "Summary": {
                "rich_text": [
                    {"text": {"content": "Test entry from Codespaces"}}
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    create_notion_entry()
