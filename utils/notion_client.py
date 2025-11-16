import os
import requests
from datetime import datetime

# ============================================================
# Notion Client – create / update / upsert / query / append-safe
# ============================================================

class NotionClient:
    def __init__(self, token=None, default_db=None):
        """汎用 Notion API クライアント"""
        self.token = token or os.environ.get("NOTION_TOKEN_AUTOJOURNAL")
        self.default_db = default_db or os.environ.get("NOTION_DB_AUTOJOURNAL_ID")

        if not self.token:
            raise ValueError("ERROR: Notion Token が設定されていません")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    # ============================================================
    # 型自動変換
    # ============================================================

    def _convert_value(self, value):
        """Python の値 → Notion Property に自動変換"""

        # datetime → Notion Date
        if isinstance(value, datetime):
            return {"date": {"start": value.isoformat()}}

        # bool
        if isinstance(value, bool):
            return {"checkbox": value}

        # 数値
        if isinstance(value, (int, float)):
            return {"number": value}

        # 文字列（日付判定込み）
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value)
                return {"date": {"start": parsed.isoformat()}}
            except Exception:
                return {"rich_text": [{"type": "text", "text": {"content": value}}]}

        # fallback → 文字列
        return {"rich_text": [{"type": "text", "text": {"content": str(value)}}]}

    def _build_properties(self, data_dict):
        props = {}
        for key, val in data_dict.items():
            props[key] = self._convert_value(val)
        return props

    # ============================================================
    # CREATE
    # ============================================================

    def create(self, database_id=None, **properties):
        database_id = database_id or self.default_db
        url = "https://api.notion.com/v1/pages"

        payload = {
            "parent": {"database_id": database_id},
            "properties": self._build_properties(properties),
        }

        res = requests.post(url, headers=self.headers, json=payload)
        return res.json()

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, page_id, **properties):
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {"properties": self._build_properties(properties)}
        res = requests.patch(url, headers=self.headers, json=payload)
        return res.json()

    # ============================================================
    # UPSERT
    # ============================================================

    def upsert(self, database_id=None, match_key=None, match_value=None, **properties):
        if match_key is None:
            raise ValueError("upsert には match_key が必要です")

        database_id = database_id or self.default_db
        existing = self.find_page_by_key(database_id, match_key, match_value)

        if existing:
            return self.update(existing["id"], **properties)

        return self.create(database_id, **properties)

    # ============================================================
    # FIND
    # ============================================================

    def find_page_by_key(self, database_id, key_name, key_value):
        database_id = database_id or self.default_db
        url = f"https://api.notion.com/v1/databases/{database_id}/query"

        query = {
            "filter": {
                "property": key_name,
                "rich_text": {"equals": str(key_value)},
            }
        }

        res = requests.post(url, headers=self.headers, json=query).json()
        results = res.get("results", [])

        return results[0] if results else None

    # ============================================================
    # UTIL：ページの既存テキストを取得する
    # ============================================================

    def _get_rich_text(self, page, field):
        """該当フィールドの plain_text を返す"""
        try:
            prop = page["properties"][field]
            rich = prop.get("rich_text", [])
            return "".join([x["plain_text"] for x in rich])
        except:
            return ""

    # ============================================================
    # APPEND：既存フィールドに追記（Prepend/Append 切替可）
    # ============================================================

    def append_text(self, page_id, field_name, text, mode="append"):
        """
        mode="append" → 既存末尾に追記
        mode="prepend" → 先頭に追記
        """

        # 1. 既存データ読み込み
        page = self.get_page(page_id)
        current = self._get_rich_text(page, field_name)

        # 2. 新しい本文生成
        if mode == "append":
            combined = current + "\n" + text if current else text
        else:
            combined = text + "\n" + current if current else text

        # 3. UPDATE
        return self.update(page_id, **{field_name: combined})

    # ============================================================
    # GET PAGE（汎用）
    # ============================================================

    def get_page(self, page_id):
        url = f"https://api.notion.com/v1/pages/{page_id}"
        res = requests.get(url, headers=self.headers)
        return res.json()
