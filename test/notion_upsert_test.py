from utils.notion_client import NotionClient
from datetime import datetime

client = NotionClient()

print("=== UPSERT TEST ===")
res = client.upsert(
    match_key="Key",
    match_value="dev-test-001",
    Category="テスト",
    Summary="Upsert 正常動作チェック",
    Details="Codespace から upsert 実行",
    UpdatedAt=datetime.now(),
)

print(res)
