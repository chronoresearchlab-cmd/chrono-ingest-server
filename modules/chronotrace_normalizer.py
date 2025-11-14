import re

class ChronoTraceNormalizer:
    """
    ChronoTrace Key Normalizer v1
    - Removes emoji / non-ASCII
    - Converts unsafe chars to "_"
    - Ensures keys start with letter or underscore
    - Ensures measurement names not starting with digit
    """

    def __init__(self, default_value="Unknown"):
        self.default_value = default_value

    # -------------------------------
    # 1. Key（measurement/tag/field名）を正規化
    # -------------------------------
    def normalize_key(self, raw: str) -> str:
        if not raw:
            return self.default_value

        # Remove emoji / non-ASCII
        normalized = re.sub(r"[^\x00-\x7F]+", "", raw)

        # Replace all unsafe chars with "_"
        normalized = re.sub(r"[^A-Za-z0-9_]", "_", normalized)

        # If begins with digit → add prefix "M_"
        if re.match(r"^[0-9]", normalized):
            normalized = "M_" + normalized

        return normalized or self.default_value

    # -------------------------------
    # 2. Value の文字列化（安全処理）
    # -------------------------------
    def normalize_value(self, v):
        return str(v)

    # -------------------------------
    # 3. 数値っぽい値は float に変換
    # -------------------------------
    def _auto_cast(self, v):
        try:
            return float(v)
        except:
            return str(v)

    # -------------------------------
    # 4. Fields 全体の正規化
    # -------------------------------
    def normalize_fields(self, fields: dict) -> dict:
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
