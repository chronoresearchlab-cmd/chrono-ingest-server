import sys
import os

# プロジェクトのルートディレクトリを import パスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.notion_client import NotionClient
from datetime import datetime

client = NotionClient()

DEVLOG_DB = os.environ["NOTION_DB_DEVLOG_ID"]

KEY = "20251116-Dev"

# Step 1: page を upsert
res = client.upsert(
    database_id=DEVLOG_DB,
    match_key="Key",
    match_value=KEY,
    Key=KEY,
    Category="DevLog",
    Summary="初回テスト (upsert)",
    Details="このエントリは upsert により作成されました。",
    Date=datetime.now(),
)
print("Upsert:", res)

# Step 2: append で追記
page = client.find_page_by_key(DEVLOG_DB, "Key", KEY)
if page:
    page_id = page["id"]
    res = client.append_text(
        page_id,
        field_name="Details",
        text="append の動作確認：追記成功。",
        mode="append",
    )
    print("Append:", res)
else:
    print("Page not found")
