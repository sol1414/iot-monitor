API_SERVER_ADDRESS = "http://localhost:8000"

# ハートビート3回分を超えたらオフライン判定
ONLINE_THRESHOLD_SEC = 90

# Live temperatureの更新間隔（秒）
LIVE_TEMP_UPDATE_INTERVAL_SEC = 10

# 記録用のDB保存イベントを検知するための閾値（秒）
DB_SAVE_DETECT_THRESHOLD_SEC = 30

# Chartの閾値設定
THRESHOLDS = {
    "temperature": {"min": 15.0, "max": 28.0},
}
SENSOR_COLUMNS = ["temperature", "humidity", "co2", "lux"]