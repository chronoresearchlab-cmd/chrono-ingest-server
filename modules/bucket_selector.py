# modules/bucket_selector.py

def bucket_selector(mode: str | None, requested_bucket: str | None):
    """
    mode: "sandbox" or "prod"
    requested_bucket: user指定の bucket（優先）
    """

    # ユーザー指定があれば優先
    if requested_bucket:
        return requested_bucket

    # sandbox / prod の自動切替
    if mode == "sandbox":
        return "chrono_test"
    else:
        return "chrono_trace"
