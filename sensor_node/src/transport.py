import json
import time
import urequests
import config
from led import blink


def _post_json(url, payload):
    """JSON POSTを実行してレスポンスを返す（呼び出し元でclose()すること）"""
    body = json.dumps(payload)
    headers = {"Content-Type": "application/json"}
    return urequests.post(url, data=body, headers=headers)


def send_heartbeat(payload):
    """
    ハートビート（ライブテレメトリ）をサーバーに送信する。
    失敗してもスキップ（リトライなし）。
    """
    try:
        res = _post_json(config.HEARTBEAT_URL, payload)
        print(f"[INFO] ハートビート送信: {payload.get('node_id')} temp={payload.get('temperature')}")
        res.close()
    except Exception as e:
        print(f"[WARN] ハートビート送信失敗: {e}")


def send_data(payload):
    """
    JSONデータをサーバーにPOST送信する（リトライ付き）

    Returns:
        bool: 送信成功/失敗
    """
    for attempt in range(1, config.SEND_RETRY_COUNT + 1):
        try:
            res = _post_json(config.SERVER_URL, payload)
            if res.status_code == 200:
                print(f"[INFO] 送信成功: {payload}")
                res.close()
                return True
            print(f"[WARN] サーバーエラー: HTTP {res.status_code}")
            res.close()
        except Exception as e:
            print(f"[WARN] 送信失敗 ({attempt}/{config.SEND_RETRY_COUNT}): {e}")

        if attempt < config.SEND_RETRY_COUNT:
            time.sleep_ms(config.SEND_RETRY_DELAY_MS)

    print("[ERROR] 全リトライ失敗")
    blink(config.LED_BLINK_COUNT_NETWORK)
    return False
