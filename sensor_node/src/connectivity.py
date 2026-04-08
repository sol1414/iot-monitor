import time
import network
import ntptime
import urequests
import config
import datetime_util
from led import led, blink


def connect_wifi():
    """
    Pi 4 の AP へ Wi-Fi 接続する。接続できるまで無限リトライ。
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    while not wlan.isconnected():
        print(f"[INFO] Wi-Fi接続中: {config.WIFI_SSID}")
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        timeout = config.WIFI_TIMEOUT_SEC
        while timeout > 0 and not wlan.isconnected():
            time.sleep(1)
            timeout -= 1

        if not wlan.isconnected():
            print("[WARN] Wi-Fi接続タイムアウト。再試行します...")
            blink(config.LED_BLINK_COUNT_NETWORK)
            time.sleep(5)

    print(f"[INFO] Wi-Fi接続完了: {wlan.ifconfig()}")
    led.on()


def sync_time():
    """
    時刻を同期してRTCをセットする。
    """
    # --- 1. NTP ---
    try:
        ntptime.host = config.NTP_HOST
        ntptime.settime()
        print("[INFO] NTP時刻同期完了")
        return
    except Exception as e:
        print(f"[WARN] NTP同期失敗: {e}")

    # --- 2. Pi 4 サーバー（RTC）からフォールバック ---
    try:
        res = urequests.get(config.TIME_URL, timeout=5)
        data = res.json()
        res.close()
        utc_str = data["utc"]
        datetime_util.set_rtc_from_iso(utc_str)
        print(f"[INFO] サーバーRTCから時刻同期完了: {utc_str}")
    except Exception as e:
        print(f"[WARN] サーバー時刻取得失敗（スキップ）: {e}")


def get_timestamp():
    """
    現在時刻を ISO 8601 形式（JST）で返す。
    RTC がセット済みであれば正確な時刻を返す。

    Returns:
        str: "2026-04-08T12:34:56+09:00"
    """
    t = time.time() + config.TIMEZONE_OFFSET_SEC
    tm = time.gmtime(t)
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}+09:00".format(*tm[:6])
