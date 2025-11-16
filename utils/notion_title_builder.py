# utils/notion_title_builder.py

from typing import Dict, Any

class TitleBuilder:
    @staticmethod
    def generate(props: Dict[str, Any]) -> str:
        category = "未分類"
        if "Category" in props:
            cat = props["Category"]
            if isinstance(cat, list) and len(cat):
                category = cat[0]

        key = props.get("Key", "no-key")
        summary = props.get("Summary", "")
        details = props.get("Details", "")

        base = f"[{category}] {key}"
        if summary:
            base += f" — {summary}"
        elif details:
            base += f" — {details[:20]}..."

        return base
