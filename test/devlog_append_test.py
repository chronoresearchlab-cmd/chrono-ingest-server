import sys
import os

# プロジェクト root を sys.path に追加
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from utils.notion_client import NotionClient

client = NotionClient()

devlog_data = {
    "Category": ["開発"],
    "Key": "test-key-001",
    "Details": "これは append テスト",
}

res = client.upsert_page(
    database_id=os.getenv("NOTION_DB_DEVLOG_ID"),
    key_property="Key",
    key_value=devlog_data["Key"],
    properties=devlog_data,
)

print("Upsert result:", res)
