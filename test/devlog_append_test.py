# test/devlog_append_test.py

import os
from utils.notion_client import NotionClient

DB_ID = os.environ["NOTION_DB_DEVLOG_ID"]

client = NotionClient()

devlog_data = {
    "Category": ["開発"],
    "Key": "test-key-001",
    "Details": "初期登録テスト",
    "Summary": "Appendテスト",
}

# まず upsert で登録
props = {
    "Category": client._build_property("multi_select", devlog_data["Category"])["multi_select"],
    "Key": {"rich_text": [{"type": "text", "text": {"content": devlog_data["Key"]}}]},
    "Details": {"rich_text": [{"type": "text", "text": {"content": devlog_data["Details"]}}]},
    "Summary": {"rich_text": [{"type": "text", "text": {"content": devlog_data["Summary"]}}]},
}

client.upsert_page(
    database_id=DB_ID,
    key_property="Key",
    key_value=devlog_data["Key"],
    properties=props
)

# Append
append_res = client.append_to_page(
    database_id=DB_ID,
    key_property="Key",
    key_value="test-key-001",
    append_text="append の2行目だよ"
)

print("Append OK:", append_res)
