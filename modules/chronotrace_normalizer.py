# modules/chronotrace_normalizer.py

class ChronoTraceNormalizer:

    def normalize_dict(self, payload: dict) -> dict:
        """
        ChronoTrace Key Normalization
        measurement/tags/fields をすべて正規化し、
        InfluxDB に書き込める形式に整える。
        """

        return {
            "measurement": self._norm_key(payload.get("measurement", "unknown")),
            "tags": {self._norm_key(k): str(v) for k, v in payload.get("tags", {}).items()},
            "fields": {
                self._norm_key(k): self._auto_cast(v)
                for k, v in payload.get("fields", {}).items()
            },
            "timestamp": payload.get("timestamp")
        }

    # -------------------------------
    # internal helpers
    # -------------------------------
    def _norm_key(self, raw: str) -> str:
        if raw is None:
            return "unknown"

        key = str(raw)
        key = key.replace(" ", "_")
        key = ''.join(c for c in key if c.isascii())

        key = ''.join(c if (c.isalnum() or c == "_") else "_" for c in key)

        if len(key) > 0 and key[0].isdigit():
            key = "M_" + key

        return key if key != "" else "unknown"

    def _auto_cast(self, v):
        try:
            return float(v)
        except:
            return str(v)            normalized = "M_" + normalized

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
