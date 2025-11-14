# modules/chronotrace_normalizer.py
import re

class ChronoTraceNormalizer:

    def __init__(self, default_value="Unknown"):
        self.default_value = default_value

    def normalize_key(self, raw: str) -> str:
        if not raw:
            return self.default_value

        s = re.sub(r"[^\x00-\x7F]+", "", raw)
        s = re.sub(r"[^A-Za-z0-9_]", "_", s)

        if re.match(r"^[0-9]", s):
            s = "M_" + s

        return s or self.default_value

    def normalize_value(self, v):
        return str(v)

    def normalize_fields(self, fields: dict):
        out = {}
        for k, v in fields.items():
            nk = self.normalize_key(k)
            try:
                nv = float(v)
            except:
                nv = v
            out[nk] = nv
        return out
