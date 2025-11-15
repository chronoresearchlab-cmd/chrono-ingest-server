import os
import requests
from datetime import datetime

# --- Secrets (Codespaces / GitHub Secrets から読み込み) ---
NOTION_TOKEN = os.environ.get("NOTION_TOKEN_AUTOJOURNAL")
DATABASE_ID = os.environ.get("NOTION_DB_AUTOJOURNAL_ID")

def create_notion_entry():
    """Auto-Journal 用の最小 Notion 書き込みテスト"""

    if not NOTION_TOKEN:
        print("ERROR: NOTION_TOKEN_AUTOJOURNAL が読み込めていません")
        return

    if not DATABASE_ID:
        print("ERROR: NOTION_DB_AUTOJOURNAL_ID が読み込めていません")
        return

    print("Secrets 読み込み OK")

    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": f"Test Entry {now}"}}]},
            "Note": {"rich_text": [{"text": {"content": "Auto-Journal Push Test"}}]}
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print(response.text)


if __name__ == "__main__":
    create_notion_entry()
