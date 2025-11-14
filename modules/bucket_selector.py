# bucket_selector.py
# ChronoNeura Influx Bucket Selector v1
#
# - "sandbox" または "prod" を安全に選択
# - Fly.io の環境変数に完全準拠
# - mode が変でも絶対に落ちない（フォールバック = 本番）


import os


class BucketSelector:
    """
    ChronoNeura Bucket Selector
    - mode = "sandbox" → INFLUX_BUCKET_SANDBOX
    - mode = "prod" または None → INFLUX_BUCKET
    - 不正値 → prod へ安全フォールバック
    """

    def __init__(self):
        self.bucket_prod = os.getenv("INFLUX_BUCKET", "chrono_trace")
        self.bucket_sandbox = os.getenv("INFLUX_BUCKET_SANDBOX", "chrono_test")

    def select(self, mode: str | None) -> str:
        """
        Selects the proper bucket depending on mode.
        Valid modes:
            - "sandbox"
            - "prod"
            - None → defaults to prod
        """

        if mode is None:
            return self.bucket_prod

        m = str(mode).strip().lower()

        # sandbox 明示指定
        if m == "sandbox":
            return self.bucket_sandbox

        # 明示 prod または不正値 → prod
        return self.bucket_prod


# Singleton instance for easy import
bucket_selector = BucketSelector()
