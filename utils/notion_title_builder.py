# utils/notion_title_builder.py
"""
Notion Title / Narrative Generator
ChronoNeura-Compatible
"""

from typing import Dict, Any


def generate_title(props: Dict[str, Any]) -> str:
    """
    Props から Notion Title を自動生成する。
    ChronoNeura Narrative の軽量ロジック。
    """

    # ---- Category: multi_select の最初 ----
    category = "未分類"
    if "Category" in props:
        cat = props["Category"]
        if isinstance(cat, list) and len(cat) > 0:
            category = cat[0]

    # ---- Key ----
    key = props.get("Key", "no-key")

    # ---- Summary / Details ----
    summary = ""
    if "Summary" in props and props["Summary"]:
        summary = props["Summary"]
    elif "Details" in props and props["Details"]:
        summary = props["Details"]

    summary = summary.replace("\n", " ")
    if len(summary) > 40:
        summary = summary[:40] + "…"

    return f"[{category}] {key} — {summary}"
