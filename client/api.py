import os
import httpx
from config import API_SERVER_ADDRESS

# この辺のアドレスは後々DNSサーバーを立てるなどして、より実践的なものにしていきたい
SERVER_URL = os.getenv("IOT_SERVER_URL", API_SERVER_ADDRESS)

def api_get(path: str):
    resp = httpx.get(f"{SERVER_URL}{path}", timeout=10.0)
    resp.raise_for_status()
    return resp.json()
