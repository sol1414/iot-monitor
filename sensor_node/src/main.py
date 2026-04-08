import time
import network
import config
import sensor
from led import led, blink
from connectivity import connect_wifi, sync_time, get_timestamp
from transport import send_data, send_heartbeat


def _is_due(now, last_ms, interval_sec):
    return time.ticks_diff(now, last_ms) >= interval_sec * 1000


def _build_payload(ds, roms):
    payload = {"node_id": config.NODE_ID, "timestamp": get_timestamp()}
    payload.update(sensor.read_all_sensors(ds, roms))
    return payload


def main():
    print("[INFO] システム起動")

    connect_wifi()
    sync_time()

    try:
        ds, roms = sensor.init_ds18b20()
    except Exception as e:
        print(f"[ERROR] センサ初期化失敗: {e}")
        while True:
            blink(config.LED_BLINK_COUNT_SENSOR)
            time.sleep(5)

    print("[INFO] 計測ループ開始")

    # 起動直後に即実行されるよう、インターバル分だけ過去に設定
    last_heartbeat_ms = time.ticks_add(
        time.ticks_ms(), -(config.HEARTBEAT_INTERVAL_SEC * 1000)
    )
    last_measurement_ms = time.ticks_add(
        time.ticks_ms(), -(config.MEASUREMENT_INTERVAL_SEC * 1000)
    )

    while True:
        now = time.ticks_ms()

        # Wi-Fi再接続チェック
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            print("[WARN] Wi-Fi切断。再接続します...")
            led.off()
            connect_wifi()

        heartbeat_due = _is_due(now, last_heartbeat_ms, config.HEARTBEAT_INTERVAL_SEC)
        measurement_due = _is_due(now, last_measurement_ms, config.MEASUREMENT_INTERVAL_SEC)

        if heartbeat_due or measurement_due:
            payload = _build_payload(ds, roms)

            if heartbeat_due:
                send_heartbeat(payload)
                last_heartbeat_ms = now

            if measurement_due:
                if payload.get("temperature") is None:
                    print("[WARN] 全センサ読み取り失敗。送信スキップ。")
                    blink(config.LED_BLINK_COUNT_SENSOR)
                else:
                    send_data(payload)
                last_measurement_ms = now

        time.sleep_ms(500)


main()
