#  Wi-Fi設定（Pi 4のAPに接続）
WIFI_SSID = "pigfarm-ap"
WIFI_PASSWORD = "pigfarm123"
WIFI_TIMEOUT_SEC = 30

#  サーバー設定（Pi 4のIP）
SERVER_URL = "http://192.168.50.1:8000/data"
REQUEST_TIMEOUT_SEC = 10

#  ノード識別 
NODE_ID = "node01"  # 複数台設置時はnode02, node03... と変更

#  測定間隔 
MEASUREMENT_INTERVAL_SEC = 10

#  DS18B20 設定（1-Wire）
DS18B20_PIN = 22
DS18B20_RESOLUTION = 12

#  ハートビート設定（ライブテレメトリ）
HEARTBEAT_INTERVAL_SEC = 1
HEARTBEAT_URL = "http://192.168.50.1:8000/heartbeat"

#  時刻同期設定（RTC）
TIME_URL = "http://192.168.50.1:8000/time"  # NTP失敗時のフォールバック

#  リトライ設定 
SENSOR_RETRY_COUNT = 3
SENSOR_RETRY_DELAY_MS = 500
SEND_RETRY_COUNT = 3
SEND_RETRY_DELAY_MS = 2000

#  NTP設定 
NTP_HOST = "pool.ntp.org"
TIMEZONE_OFFSET_SEC = 9 * 3600  # JST（UTC+9）

#  LEDエラー表示 
LED_BLINK_INTERVAL_MS = 200
LED_BLINK_COUNT_SENSOR = 3   # センサエラー：3回点滅
LED_BLINK_COUNT_NETWORK = 5  # ネットワークエラー：5回点滅
