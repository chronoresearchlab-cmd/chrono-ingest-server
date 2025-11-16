import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List


class NotionClient:
    """
    Notion API 用ミニマルクライアント（Create / Update / Upsert / Append 対応）
    """

    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN_AUTOJOURNAL")
        if not self.token:
            raise RuntimeError("ERROR: NOTION_TOKEN_AUTOJOURNAL が読み込めませんでした")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    # --------------------------------------------------
    # 内部ユーティリティ
    # --------------------------------------------------

    def _request(self, method: str, url: str, data: Optional[Dict] = None):
        endpoint = f"https://api.notion.com/v1{url}"
        resp = requests.request(method, endpoint, headers=self.headers, json=data)

        if not resp.ok:
            print(f"[Notion API ERROR] {resp.status_code} {resp.text}")
            return None

        return resp.json()

    def _get_page(self, page_id: str):
        return self._request("GET", f"/pages/{page_id}")

    # --------------------------------------------------
    # プロパティ生成ユーティリティ
    # --------------------------------------------------

    def _build_property(self, field_type: str, value: Any):
        """
        Notion の各プロパティ型に応じて正しい JSON を作成する。
        """

        # ---- Rich Text ----
        if field_type == "rich_text":
            return {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": str(value)}
                    }
                ]
            }

        # ---- Title ----
        if field_type == "title":
            return {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": str(value)}
                    }
                ]
            }

        # ---- Date ----
        if field_type == "date":
            return {
                "date": {"start": value}
            }

        # ---- Multi-select ----
        if field_type == "multi_select":
            if isinstance(value, list):
                return {"multi_select": [{"name": v} for v in value]}
            else:
                return {"multi_select": [{"name": value}]}

        # ---- Select ----
        if field_type == "select":
            return {"select": {"name": str(value)}}

        # ---- Checkbox ----
        if field_type == "checkbox":
            return {"checkbox": bool(value)}

        # ---- Number ----
        if field_type == "number":
            return {"number": float(value)}

        # ---- 任意文字列 ----
        return {
            "rich_text": [
                {"type": "text", "text": {"content": str(value)}}
            ]
        }

    # --------------------------------------------------
    # Upsert（Create or Update）
    # --------------------------------------------------

    def upsert_page(
        self,
        database_id: str,
        key_property: str,
        key_value: str,
        properties: Dict[str, Any]
    ):
        """
        key_property（例: Key） が一致するページを検索 → 存在すれば Update、無ければ Create。
        """

        # ---- Search ----
        query_payload = {
            "filter": {
                "property": key_property,
                "rich_text": {"equals": key_value}
            }
        }
        search = self._request("POST", f"/databases/{database_id}/query", query_payload)

        page_id = None
        if search and search.get("results"):
            page_id = search["results"][0]["id"]

        # ---- properties を Notion JSON に変換 ----
        props_json = {}
        for prop_name, prop_value in properties.items():
            if isinstance(prop_value, tuple) and len(prop_value) == 2:
                field_type, val = prop_value
            else:
                field_type, val = ("rich_text", prop_value)

            props_json[prop_name] = self._build_property(field_type, val)

        # ---- Update or Create ----
        if page_id:
            payload = {"properties": props_json}
            return self._request("PATCH", f"/pages/{page_id}", payload)
        else:
            payload = {
                "parent": {"database_id": database_id},
                "properties": props_json
            }
            return self._request("POST", "/pages", payload)

    # --------------------------------------------------
    # Append（Rich text に追記）
    # --------------------------------------------------

    def append_to_property(self, page_id: str, property_name: str, append_text: str):
        """
        Rich text プロパティに追記する。
        """

        page = self._get_page(page_id)
        if not page:
            raise RuntimeError("Page not found")

        props = page.get("properties", {})
        if property_name not in props:
            raise ValueError(f"Property {property_name} not found")

        existing_prop = props[property_name]

        # 既存テキスト抽出
        old_text = ""
        if "rich_text" in existing_prop:
            old_text = "".join(rt.get("plain_text", "") for rt in existing_prop["rich_text"])

        new_text = old_text + "\n" + append_text

        payload = {
            "properties": {
                property_name: {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": new_text}
                        }
                    ]
                }
            }
        }

        return self._request("PATCH", f"/pages/{page_id}", payload)
