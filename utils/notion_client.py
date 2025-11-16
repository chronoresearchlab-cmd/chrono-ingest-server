import os
import requests
from datetime import datetime


class NotionClient:
    def __init__(self):
        self.token = os.environ.get("NOTION_TOKEN_AUTOJOURNAL")
        self.default_db = os.environ.get("NOTION_DB_AUTOJOURNAL_ID")

        if not self.token:
            raise ValueError("ERROR: NOTION_TOKEN_AUTOJOURNAL is missing!")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    # ---------------------------------------------
    # プロパティ value → Notion 形式へ 自動変換
    # ---------------------------------------------
    def format_property(self, key, value):
        """
        Notion DB のフィールドタイプを意識せず渡せる形式に変換する
        """
        # None は無視
        if value is None:
            return None

        # 日付
        if isinstance(value, datetime):
            return {
                "date": {
                    "start": value.isoformat()
                }
            }

        # 数値
        if isinstance(value, (int, float)):
            return {"number": value}

        # 真偽値
        if isinstance(value, bool):
            return {"checkbox": value}

        # リスト（rich_text化）
        if isinstance(value, list):
            return {
                "rich_text": [
                    {"type": "text", "text": {"content": str(v)}}
                    for v in value
                ]
            }

        # 文字列（汎用 → rich_text）
        return {
            "rich_text": [
                {"type": "text", "text": {"content": str(value)}}
            ]
        }

    # ---------------------------------------------
    # CREATE：Notion に新規ページを追加
    # ---------------------------------------------
    def create(self, database_id=None, **kwargs):
        database_id = database_id or self.default_db

        properties = {}
        for key, value in kwargs.items():
            pv = self.format_property(key, value)
            if pv:
                properties[key] = pv

        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }

        url = "https://api.notion.com/v1/pages"
        res = requests.post(url, json=payload, headers=self.headers)
        return res.json()

    # ---------------------------------------------
    # UPDATE：ページIDを指定して更新
    # ---------------------------------------------
    def update(self, page_id: str, **kwargs):
        properties = {}
        for key, value in kwargs.items():
            pv = self.format_property(key, value)
            if pv:
                properties[key] = pv

        payload = {"properties": properties}

        url = f"https://api.notion.com/v1/pages/{page_id}"
        res = requests.patch(url, json=payload, headers=self.headers)
        return res.json()

    # ---------------------------------------------
    # UPSERT：Keyプロパティが一致するページがあれば更新、なければ作成
    # ---------------------------------------------
    def upsert(self, match_key: str, match_value, database_id=None, **kwargs):
        database_id = database_id or self.default_db

        # ① まず DB から一致するページを検索
        query = {
            "filter": {
                "property": match_key,
                "rich_text": {
                    "equals": str(match_value)
                }
            }
        }

        search_url = f"https://api.notion.com/v1/databases/{database_id}/query"
        res = requests.post(search_url, json=query, headers=self.headers).json()
        results = res.get("results", [])

        # ② あれば UPDATE
        if len(results) > 0:
            page_id = results[0]["id"]
            return self.update(page_id, **kwargs)

        # ③ なければ CREATE
        return self.create(database_id, **kwargs)

def find_page_by_key(self, database_id, key_name, key_value):
    query = {
        "filter": {
            "property": key_name,
            "rich_text": {"equals": key_value}
        }
    }
    res = requests.post(
        f"{self.base_url}/databases/{database_id}/query",
        headers=self.headers,
        json=query,
    )
    data = res.json()
    return data["results"][0] if data.get("results") else None
