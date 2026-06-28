import requests

def validate_url(url, timeout=8):
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        if resp.status_code >= 400:
            return (False, "请输入正确网址，当前网址无法访问")
        return (True, "")
    except requests.ConnectionError:
        return (False, "请输入正确网址，无法连接到该地址")
    except requests.Timeout:
        return (False, "请输入正确网址，连接超时")
