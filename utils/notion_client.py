# utils/notion_client.py
"""
ChronoNeura SyncBridge – Notion Writer 正式版（TitleBuilder 分離構造）
"""

import os
from typing import Dict, Any, Optional

from notion_client import Client
from utils.notion_title_builder import TitleBuilder


# ============================================================
# Trace層：Notion API の低レベルクラス（通信・変換のみ）
# ============================================================
class NotionClientCore:
    """Notion API の生I/O層"""

    def __init__(self, token_env="NOTION_TOKEN_AUTOJOURNAL"):
        token = os.getenv(token_env)
        if not token:
            raise RuntimeError(f"環境変数 {token_env} が未設定です。")

        self.client = Client(auth=token)

    # --- property builder ---
    def build_prop(self, t: str, v: Any):
        if v is None:
            return None

        if t == "title":
            return {"title": [{"text": {"content": str(v)}}]}

        if t == "rich_text":
            return {"rich_text": [{"text": {"content": str(v)}}]}

        if t == "multi_select":
            if isinstance(v, str):
                v = [v]
            return {"multi_select": [{"name": x} for x in v]}

        return {"rich_text": [{"text": {"content": str(v)}}]}

    # --- create ---
    def create_page(self, db_id: str, props: Dict[str, Any]):
        return self.client.pages.create(
            parent={"database_id": db_id},
            properties=props
        )

    # --- update ---
    def update_page(self, page_id: str, props: Dict[str, Any]):
        return self.client.pages.update(page_id, properties=props)

    # --- query ---
    def query_by_key(self, db_id: str, key: str, value: str):
        res = self.client.databases.query(
            database_id=db_id,
            filter={"property": key, "rich_text": {"equals": value}}
        )
        arr = res.get("results", [])
        return arr[0] if arr else None


# ============================================================
# SyncBridge層：Writer（create / upsert / append を統合した高層）
# ============================================================
class NotionWriter(NotionClientCore):
    """外部 dict を受け取り、Notion DB へ書き込む高層 Writer"""

    def __init__(self,
                 token_env="NOTION_TOKEN_AUTOJOURNAL",
                 db_env="NOTION_DB_DEVLOG_ID"):

        super().__init__(token_env)

        db_id = os.getenv(db_env)
        if not db_id:
            raise RuntimeError(f"環境変数 {db_env} が未設定です。")

        self.db_id = db_id

    # ---------------------------------------------------------
    # create
    # ---------------------------------------------------------
    def write_create(self, data: Dict[str, Any]):
        props = self._convert(data)
        return self.create_page(self.db_id, props)

    # ---------------------------------------------------------
    # upsert（存在すれば更新・無ければ生成）
    # ---------------------------------------------------------
    def write_upsert(self, key: str, data: Dict[str, Any]):
        page = self.query_by_key(self.db_id, "Key", key)
        props = self._convert(data)

        if page:
            return self.update_page(page["id"], props)

        return self.create_page(self.db_id, props)

    # ---------------------------------------------------------
    # append（Details に追記）
    # ---------------------------------------------------------
    def write_append(self, key: str, text: str):
        page = self.query_by_key(self.db_id, "Key", key)
        if not page:
            raise RuntimeError(f"append 対象 key={key} のページが見つかりません")

        page_id = page["id"]
        existing = page["properties"]["Details"]["rich_text"]
        merged = existing + [{"text": {"content": "\n" + text}}]

        return self.update_page(
            page_id,
            {"Details": {"rich_text": merged}}
        )

    # ---------------------------------------------------------
    # 動的モード判定（create / upsert / append 自動判別）
    # ---------------------------------------------------------
    def write_dynamic(self, data: Dict[str, Any]):
        mode = data.get("mode", "create")

        if mode == "create":
            return self.write_create(data)

        if mode == "upsert":
            if "key" not in data:
                raise RuntimeError("upsert には 'key' が必要です。")
            return self.write_upsert(data["key"], data)

        if mode == "append":
            if "key" not in data or "append" not in data:
                raise RuntimeError("append には 'key' と 'append' が必要です。")
            return self.write_append(data["key"], data["append"])

        raise RuntimeError(f"未知の mode：{mode}")

    # ============================================================
    # property 変換（TitleBuilder による Title 自動生成も含む）
    # ============================================================
    def _convert(self, data: Dict[str, Any]):
        props = {}

        # --- 基本構造 ---
        if "title" in data:
            props["Title"] = self.build_prop("title", data["title"])

        if "details" in data:
            props["Details"] = self.build_prop("rich_text", data["details"])

        if "summary" in data:
            props["Summary"] = self.build_prop("rich_text", data["summary"])

        if "category" in data:
            props["Category"] = self.build_prop("multi_select", data["category"])

        if "key" in data:
            props["Key"] = self.build_prop("rich_text", data["key"])

        # --- Title 自動生成ロジック（空なら自動生成） ---
        if "Title" not in props or not props["Title"]:
            title_text = TitleBuilder.generate({
                "Category": data.get("category"),
                "Key": data.get("key"),
                "Summary": data.get("summary"),
                "Details": data.get("details"),
            })
            props["Title"] = self.build_prop("title", title_text)

        return props
