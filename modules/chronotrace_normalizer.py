import re


class ChronoTraceNormalizer:
    """
    ChronoTrace Key Normalizer v1

    - measurement / tag / field 名を安全なキーに正規化
    - 絵文字・全角など非ASCIIは削除
    - 英数字とアンダースコア以外は "_" に置換
    - 先頭が数字の measurement は "M_" を付与
    """

    def __init__(self, default_value: str = "Unknown"):
        self.default_value = default_value

    # -------------------------------
    # 1. Key（measurement / tag / field 名）を正規化
    # -------------------------------
    def normalize_key(self, raw: str) -> str:
        if not raw:
            return self.default_value

        # 絵文字・非ASCIIを削除
        normalized = re.sub(r"[^\x00-\x7F]+", "", raw)

        # 英数字と "_" 以外は "_" に置換
        normalized = re.sub(r"[^A-Za-z0-9_]", "_", normalized)

        # 先頭が数字なら "M_" を付与
        if re.match(r"^[0-9]", normalized):
            normalized = "M_" + normalized

        return normalized or self.default_value

    # -------------------------------
    # 2. Value を安全に文字列化（タグ用）
    # -------------------------------
    def normalize_value(self, v):
        return str(v)

    # -------------------------------
    # 3. 数値っぽい値は float に変換（内部用）
    # -------------------------------
    def _auto_cast(self, v):
        try:
            return float(v)
        except Exception:
            return str(v)

    # -------------------------------
    # 4. Fields 全体の正規化
    # -------------------------------
    def normalize_fields(self, fields: dict) -> dict:
        """
        fields の key を正規化しつつ、
        可能なら float にキャストして返す。
        """
        normalized = {}

        for k, v in fields.items():
            nk = self.normalize_key(k)

            # 値の型補正
            try:
                nv = float(v)
            except Exception:
                nv = v

            normalized[nk] = nv

        return normalized

    # -------------------------------
    # 5. payload 全体を正規化（main.py から呼ばれる）
    # -------------------------------
    def normalize_dict(self, raw: dict) -> dict:
        """
        {
          "measurement": "...",
          "tags": {...},
          "fields": {...},
          "timestamp": "..."
        }
        を受け取って、measurement / tags / fields を正規化して返す。
        """
        if not isinstance(raw, dict):
            raise ValueError("payload must be dict")

        # measurement
        m_raw = raw.get("measurement", "unknown")
        measurement = self.normalize_key(m_raw)

        # tags
        tags_raw = raw.get("tags", {}) or {}
        tags = {}
        for k, v in tags_raw.items():
            nk = self.normalize_key(k)
            tags[nk] = self.normalize_value(v)

        # fields
        fields_raw = raw.get("fields", {}) or {}
        fields = self.normalize_fields(fields_raw)

        # timestamp はそのまま通す（ISO 文字列想定）
        timestamp = raw.get("timestamp")

        return {
            "measurement": measurement,
            "tags": tags,
            "fields": fields,
            "timestamp": timestamp,
        }
