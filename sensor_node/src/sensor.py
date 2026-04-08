import time
from machine import Pin
import onewire
import ds18x20
import config

# DS18B20 解像度ビット数 → 変換待機時間（ms）の対応表
_CONVERSION_MS = {9: 94, 10: 188, 11: 375, 12: 750}


def init_ds18b20():
    """DS18B20センサを初期化して（bus, roms）を返す"""
    ow = onewire.OneWire(Pin(config.DS18B20_PIN))
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()
    if not roms:
        raise RuntimeError("DS18B20が見つかりません。配線を確認してください。")
    print(f"[INFO] DS18B20 検出: {len(roms)}台")
    return ds, roms


def read_temperature(ds, roms):
    """DS18B20から温度を読み取る（1台目のセンサを使用）"""
    ds.convert_temp()
    time.sleep_ms(_CONVERSION_MS.get(config.DS18B20_RESOLUTION, 750))
    temp = ds.read_temp(roms[0])
    if temp is None or not (-55.0 <= temp <= 125.0):
        raise RuntimeError(f"DS18B20 無効値: {temp}")
    return round(temp, 2)


def read_all_sensors(ds, roms):
    """全センサからデータを読み取り辞書で返す（リトライ付き）"""
    return {
        "temperature": _read_with_retry(
            "DS18B20 温度",
            lambda: read_temperature(ds, roms)
        ),
    }


def _read_with_retry(sensor_name, read_func):
    """センサ読み取りをリトライ付きで実行。全失敗時は None を返す"""
    for attempt in range(1, config.SENSOR_RETRY_COUNT + 1):
        try:
            return read_func()
        except Exception as e:
            print(f"[WARN] {sensor_name} 失敗 ({attempt}/{config.SENSOR_RETRY_COUNT}): {e}")
            if attempt < config.SENSOR_RETRY_COUNT:
                time.sleep_ms(config.SENSOR_RETRY_DELAY_MS)
    print(f"[ERROR] {sensor_name} 全リトライ失敗")
    return None
