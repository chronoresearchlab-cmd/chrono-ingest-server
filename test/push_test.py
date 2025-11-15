import os
import requests
import json

NOTION_TOKEN = os.environ["NOTION_TOKEN_AUTOJOURNAL"]
DB_ID = os.environ["NOTION_DB_AUTOJOURNAL_ID"]

url = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ← push_test に存在しているプロパティ名に合わせている
payload = {
    "parent": {"database_id": DB_ID},
    "properties": {
        "date": { "date": { "start": "2025-11-15" } },
        "Event": { "title": [ { "text": { "content": "API push test" } } ] },
        "Narrative": { "rich_text": [ { "text": { "content": "Hello from fly.io" } } ] },
        "number": { "number": 1 }
    }
}

res = requests.post(url, headers=headers, json=payload)

print("STATUS:", res.status_code)
print(res.text)
