import os
import json
import requests
from typing import Dict, Any, Optional


class NotionClient:
    """
    Notion API wrapper supporting:
    - create page
    - update page
    - upsert (search by Key → update or create)
    - append (for Details rich_text)
    """

    def __init__(self, notion_token: Optional[str] = None):
        self.token = notion_token or os.environ.get("NOTION_TOKEN_AUTOJOURNAL")
        if not self.token:
            raise ValueError("Missing Notion token (NOTION_TOKEN_AUTOJOURNAL)")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    # --------------------------------------------------------
    # 共通 request
    # --------------------------------------------------------
    def _request(self, method: str, url: str, payload: Dict[str, Any]):
        r = requests.request(method, url, headers=self.headers, data=json.dumps(payload))
        if not r.ok:
            raise Exception(f"Notion API Error: {r.text}")
        return r.json()

    # --------------------------------------------------------
    # property builder（型に応じて Notion JSON を生成）
    # --------------------------------------------------------
    def _build_property(self, field_type: str, value: Any) -> Dict[str, Any]:
        if value is None:
            return {}

        # --- multi_select（重要） ---
        if field_type == "multi_select":
            if isinstance(value, str):
                options = [{"name": value}]
            elif isinstance(value, (list, tuple)):
                options = [{"name": v} for v in value]
            else:
                options = [{"name": str(value)}]
            return {"multi_select": options}

        # --- title ---
        if field_type == "title":
            return {
                "title": [
                    {"type": "text", "text": {"content": str(value)}}
                ]
            }

        # --- rich_text ---
        if field_type == "rich_text":
            return {
                "rich_text": [
                    {"type": "text", "text": {"content": str(value)}}
                ]
            }

        # --- date ---
        if field_type == "date":
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            return {"date": {"start": value}}

        # fallback（すべて rich_text にする）
        return {
            "rich_text": [
                {"type": "text", "text": {"content": str(value)}}
            ]
        }

    # --------------------------------------------------------
    # Create
    # --------------------------------------------------------
    def create_page(self, database_id: str, properties: Dict[str, Any]):
        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }
        return self._request("POST", url, payload)

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------
    def update_page(self, page_id: str, properties: Dict[str, Any]):
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {"properties": properties}
        return self._request("PATCH", url, payload)

    # --------------------------------------------------------
    # Search → Key が一致するページを探す
    # --------------------------------------------------------
    def find_page_by_key(self, database_id: str, key_property: str, key_value: str):
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        payload = {
            "filter": {
                "property": key_property,
                "rich_text": {"equals": key_value},
            }
        }
        res = self._request("POST", url, payload)
        results = res.get("results", [])
        return results[0] if results else None

    # --------------------------------------------------------
    # Upsert（存在すれば update、無ければ create）
    # --------------------------------------------------------
    def upsert_page(
        self,
        database_id: str,
        key_property: str,
        key_value: str,
        properties: Dict[str, Any]
    ):
        found = self.find_page_by_key(database_id, key_property, key_value)

        if found:
            page_id = found["id"]
            return self.update_page(page_id, properties)

        return self.create_page(database_id, properties)

    # --------------------------------------------------------
    # Append：Details に追記（改行付き）
    # --------------------------------------------------------
    def append_to_page(self, database_id: str, key_property: str, key_value: str, append_text: str):
        page = self.find_page_by_key(database_id, key_property, key_value)
        if not page:
            raise ValueError("Page not found for append.")

        page_id = page["id"]
        existing = page["properties"].get("Details", {}).get("rich_text", [])

        merged = existing + [
            {"type": "text", "text": {"content": "\n" + append_text}}
        ]

        payload = {"properties": {"Details": {"rich_text": merged}}}
        url = f"https://api.notion.com/v1/pages/{page_id}"
        return self._request("PATCH", url, payload)
