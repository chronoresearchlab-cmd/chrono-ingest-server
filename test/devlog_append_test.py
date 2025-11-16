# test/devlog_append_test.py
# ------------------------------------------------------------
# ChronoNeura DevLog 用 Notion Append テスト（完全安定版）　
# ------------------------------------------------------------

import sys
import os

# --- import パスをプロジェクトルートに固定（最重要） ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.notion_client import NotionClient


# --- Secrets / DB ID ---
DB_ID = os.environ.get("NOTION_DB_DEVLOG_ID")
if not DB_ID:
    raise RuntimeError("環境変数 NOTION_DB_DEVLOG_ID が設定されていません。")


# --- テストデータ ---
KEY_VALUE = "test-key-001"

devlog_data = {
    "Category": ["開発"],
    "Key": KEY_VALUE,
    "Details": "初回登録テスト（upsert）",
    "Summary": "Summary の初期値",
}


# ------------------------------------------------------------
# 1) Notion ページを upsert（更新 or 新規作成）
# ------------------------------------------------------------
def build_properties(client, data):
    """NotionClient の public API に合わせて property dict を生成する"""
    return {
        "Category": client._build_property("multi_select", data["Category"]),
        "Key": client._build_property("rich_text", data["Key"]),
        "Details": client._build_property("rich_text", data["Details"]),
        "Summary": client._build_property("rich_text", data["Summary"]),
    }


def main():
    client = NotionClient()

    print("=== Step1: upsert 実行 ===")

    props = build_properties(client, devlog_data)

    res_upsert = client.upsert_page(
        database_id=DB_ID,
        key_property="Key",
        key_value=KEY_VALUE,
        properties=props,
    )
    print("[upsert OK]", res_upsert)

    # ------------------------------------------------------------
    # 2) append：Details に追記
    # ------------------------------------------------------------
    print("=== Step2: append 実行 ===")

    append_text = "append の2行目です。テスト完了！"

    res_append = client.append_to_page(
        database_id=DB_ID,
        key_property="Key",
        key_value=KEY_VALUE,
        append_text=append_text,
    )
    print("[append OK]", res_append)


if __name__ == "__main__":
    main()
