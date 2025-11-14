import re

class ChronoTraceNormalizer:
    """
    ChronoTrace Key Normalization Processor
    Implements: ChronoTrace_KeyNormalizationPolicy_v1
    """

    def __init__(self, default="Unknown"):
        self.default = default

    def normalize_key(self, raw: str) -> str:
        """Normalize measurement/tag/field keys safely."""
        if raw is None or raw == "":
            return self.default

        # 1. Remove emoji / multibyte chars
        normalized = re.sub(r"[^\x00-\x7F]+", "", raw)

        # 2. Replace forbidden symbols with '_'
        normalized = re.sub(r"[^A-Za-z0-9_]", "_", normalized)

        # 3. Prepend 'M_' if starting with number
        if re.match(r"^[0-9]", normalized):
            normalized = "M_" + normalized

        return normalized or self.default

    def normalize_dict(self, data: dict) -> dict:
        return {self.normalize_key(k): v for k, v in data.items()}

    def normalize_measurement(self, name: str) -> str:
        return self.normalize_key(name)

    def normalize_tags(self, tags: dict) -> dict:
        return self.normalize_dict(tags)

    def normalize_fields(self, fields: dict) -> dict:
        return self.normalize_dict(fields)
