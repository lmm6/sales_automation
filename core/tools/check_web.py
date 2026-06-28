import re

def validate_url(url, timeout=8):
    """Validate URL format only. Actual connectivity is checked during crawling."""
    if not url or len(url) < 5:
        return (False, "请输入正确网址")
    if not re.match(r"^https?://", url.strip()):
        return (False, "请输入正确网址，网址必须以 http:// 或 https:// 开头")
    return (True, "")
