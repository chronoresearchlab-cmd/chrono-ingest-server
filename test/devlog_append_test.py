from utils.notion_client import NotionClient

client = NotionClient()

DATABASE_ID = os.getenv("NOTION_DB_DEVLOG_ID")

# Step1: Upsert（タイトル・日付などをキーで固定）
page = client.upsert_page(
    database_id=DATABASE_ID,
    key_property="Key",
    key_value="2025-11-16",
    properties={
        "Key": {"rich_text": [{"type": "text", "text": {"content": "2025-11-16"}}]},
        "Title": {"title": [{"type": "text", "text": {"content": "DevLog 2025-11-16"}}]},
        "Category": {"multi_select": [{"name": "開発"}]},
        "Details": {"rich_text": [{"type": "text", "text": {"content": "初期生成"}}]},
    }
)

page_id = page["id"]

# Step2: Append（Details に追記）
client.append_to_page(
    page_id,
    property_name="Details",
    append_text="追記テキスト：Notion Append テスト"
)
