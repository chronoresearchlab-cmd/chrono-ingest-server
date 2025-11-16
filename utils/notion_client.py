# utils/notion_client.py
"""
汎用 Notion クライアント（Upsert / Update / Append 対応）
ChronoNeura Auto-Journal / DevLog 用の共通 Notion API ラッパー

機能：
- create_page()
- update_page()
- upsert_page()（Key=タイトルで検索 → 存在すれば更新、なければ作成）
- append_to_property()（既存テキストへ追記）

共通仕様：
- プロパティは Notion DB の型を見て自動変換
- multi_select は [{"name": value}] の配列に変換（← **今回修正ポイント**）
- rich_text は [{"type":"text","text":{"content": "..."} }] に統一
"""

import os
import requests
from datetime import datetime


class NotionClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    # -----------------------------------------------------
    # Internal API Caller
    # -----------------------------------------------------
    def _request(self, method, endpoint, json=None):
        url = f"{self.base_url}{endpoint}"
        resp = requests.request(method, url, headers=self.headers, json=json)

        if not resp.ok:
            print(f"[Notion ERROR] {resp.status_code} {resp.text}")
        return resp.json()

    # -----------------------------------------------------
    # Utility: Notion プロパティ型へ自動変換
    # -----------------------------------------------------
    def _convert_property(self, key, value, prop_type):
        """
        Notion データベースのプロパティ型に合わせて自動変換する。
        """
        # --- Title ---
        if prop_type == "title":
            return {
                "title": [{"type": "text", "text": {"content": str(value)}}]
            }

        # --- Rich Text ---
        if prop_type == "rich_text":
            return {
                "rich_text": [{"type": "text", "text": {"content": str(value)}}]
            }

        # --- Multi-select ---
        if prop_type == "multi_select":
            # 文字列単体なら ["value"] にする
            if isinstance(value, str):
                return {"multi_select": [{"name": value}]}
            # 配列なら [{"name":...}] 列に変換
            if isinstance(value, list):
                return {"multi_select": [{"name": v} for v in value]}
            raise ValueError(f"Invalid multi_select value for {key}: {value}")

        # --- Date ---
        if prop_type == "date":
            if isinstance(value, datetime):
                value = value.isoformat()
            return {"date": {"start": value}}

        # --- Toggle / Checkbox ---
        if prop_type == "checkbox":
            return {"checkbox": bool(value)}

        # --- Number ---
        if prop_type == "number":
            return {"number": float(value)}

        # --- Fallback (Auto Rich Text) ---
        return {
            "rich_text": [{"type":
