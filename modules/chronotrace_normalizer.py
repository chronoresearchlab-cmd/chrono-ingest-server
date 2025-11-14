# modules/chronotrace_normalizer.py

import re
from datetime import datetime

class ChronoTraceNormalizer:
    """
    ChronoTrace Key Normalization Module
    Implements: 🌟ChronoTrace_KeyNormalizationPolicy_v1
    """

    def __init__(self, default="Unknown"):
        self.default = default

    # -----------------------------------------------------
    # 1. measurement/tags/fields のキーを正規化
    # -----------------------------------------------------
    def normalize_key(self, raw: str) -> str:
        """
        規則:
        1) 絵文字・全角文字 → 削除
        2) 記号・空白 → "_"
        3) 英数字と "_" のみ許可
        4) 先頭が数字 → "M_" を付与
        """
        if not raw:
            return self.default

        # 絵文字・全角を削除
        normalized = re.sub(r"[^\x00-\x7F]+", "", raw)

        # 記号を "_"
        normalized = re.sub(r"[^A-Za-z0-9_]", "_", normalized)

        # 先頭数字なら M_ を付ける
        if re.match(r"^[0-9]", normalized):
            normalized = "M_" + normalized

        return normalized or self.default

    # -----------------------------------------------------
    # 2. fields 値の型補正
    # -----------------------------------------------------
    def normalize_fields(self, fields: dict) -> dict:
        """数値にできる値は数値化。その他は文字列のまま。"""
        normalized = {}
        for k, v in fields.items():
            nk = self.normalize_key(k)

            # 値の型補正
            try:
                nv = float(v)
            except:
                nv = v

            normalized[nk] = nv

        return normalized

    # -----------------------------------------------------
    # 3. Tags のキー正規化
    # -----------------------------------------------------
    def normalize_tags(self, tags: dict) -> dict:
        normalized = {}
        for k, v in tags.items():
            nk = self.normalize_key(k)
            nv = str(v)
            normalized[nk] = nv
        return normalized

    # -----------------------------------------------------
    # 4. measurement 名も正規化
    # -----------------------------------------------------
    def normalize_measurement(self, name: str) -> str:
        return self.normalize_key(name)

    # -----------------------------------------------------
    # 5. timestamp 補正
    # -----------------------------------------------------
    def normalize_timestamp(self, ts_raw: str) -> str:
        """
        timestamp を RFC3339 (InfluxDB) 形式に整形。
        raw のままの場合、"Unknown" を返さないよう注意。
        """
        try:
            dt = datetime.fromisoformat(ts_raw)
            return dt.isoformat() + "Z"
        except:
            return datetime.utcnow().isoformat() + "Z"

    # -----------------------------------------------------
    # 6. Ingest Payload 全体を正規化
    # -----------------------------------------------------
    def normalize_payload(self, payload: dict) -> dict:
        """
        期待される入力:
        {
            "measurement": "ultralight_trace",
            "tags": {...},
            "fields": {...},
            "timestamp": "2025-11-14T05:12:00"
        }
        """

        m = self.normalize_measurement(payload.get("measurement", "unknown"))
        t = self.normalize_tags(payload.get("tags", {}))
        f = self.normalize_fields(payload.get("fields", {}))
        ts = self.normalize_timestamp(payload.get("timestamp"))

        return {
            "measurement": m,
            "tags": t,
            "fields": f,
            "timestamp": ts
        }
    def normalize_fields(self, fields: dict) -> dict:
        return self.normalize_dict(fields)
