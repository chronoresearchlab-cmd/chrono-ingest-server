# utils/notion_client.py

import os
import requests
from typing import Dict, Any, Optional, List


class NotionClient:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN_AUTOJOURNAL") or os.getenv("NOTION_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    # ------------------------------
    # 低レベル API 呼び出し
    # ------------------------------
    def _request(self, method: str, url: str, payload: Dict[str, Any] = None):
        resp = requests.request(method, url, headers=self.headers, json=payload)
        if not resp.ok:
            raise Exception(
                f"Notion API Error {resp.status_code}: {resp.text}"
            )
        return resp.json()

    # ------------------------------
    # プロパティ生成ユーティリティ
    # ------------------------------
    def _build_property(self, field_type: str, value: Any):
        """
        Notion DB に合わせた動的プロパティビルダー
        """
        if field_type == "title":
            return {"title": [{"type": "text", "text": {"content": value}}]}

        if field_type == "rich_text":
            return {"rich_text": [{"type": "text", "text": {"content": value}}]}

        if field_type == "multi_select":
            if isinstance(value, list):
                return {"multi_select": [{"name": v} for v in value]}
            else:
                return {"multi_select": [{"name": value}]}

        if field_type == "select":
            return {"select": {"name": value}}

        if field_type == "number":
            return {"number": value}

        return None

    # ------------------------------
    # ページ作成
    # ------------------------------
    def create_page(self, database_id: str, properties: Dict[str, Any]):
        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }
        return self._request("POST", url, payload)

    # ------------------------------
    # Upsert（存在すれば Update、なければ Create）
    # ------------------------------
    def upsert_page(
        self,
        database_id: str,
        key_property: str,
        key_value: str,
        properties: Dict[str, Any],
    ):
        # 1) Search
        search_url = "https://api.notion.com/v1/databases/{}/query".format(database_id)

        query_payload = {
            "filter": {
                "property": key_property,
                "rich_text": {
                    "equals": key_value
                }
            }
        }

        res = self._request("POST", search_url, query_payload)

        page_id = None
        if res.get("results"):
            page_id = res["results"][0]["id"]

        # 2) Update
        if page_id:
            update_url = f"https://api.notion.com/v1/pages/{page_id}"
            payload = {"properties": properties}
            return self._request("PATCH", update_url, payload)

        # 3) Create
        return self.create_page(database_id, properties)

    # ------------------------------
    # Append（既存ページの RichText に追記）
    # ------------------------------
    def append_to_page(self, page_id: str, property_name: str, append_text: str):
        """
        Notion の rich_text プロパティにテキストを追記する
        """
        # 現在のページ内容を取得
        page_url = f"https://api.notion.com/v1/pages/{page_id}"
        page = self._request("GET", page_url, None)

        current_prop = page["properties"].get(property_name)
        if not current_prop:
            raise Exception(f"Property '{property_name}' not found in the page.")

        # すでにある rich_text
        existing = current_prop.get("rich_text", [])

        # 新しい text block を末尾に追加
        new_block = {
            "type": "text",
            "text": {"content": "\n" + append_text}
        }

        updated_text = existing + [new_block]

        update_payload = {
            "properties": {
                property_name: {
                    "rich_text": updated_text
                }
            }
        }

        update_url = f"https://api.notion.com/v1/pages/{page_id}"
        return self._request("PATCH", update_url, update_payload)
