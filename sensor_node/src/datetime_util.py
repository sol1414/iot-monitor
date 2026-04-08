import utime
from machine import RTC

_rtc = RTC()


def set_rtc_from_iso(time_str):
    """
    ISO 8601文字列（UTC）からRTCをセットする。

    対応フォーマット:
      "2026-04-08T11:30:00Z"
      "2026-04-08T11:30:00+00:00"
      "2026-04-08T11:30:00.123456Z"
    """
    year, month, day, hour, minute, second = _parse_iso8601(time_str)
    ts = utime.mktime((year, month, day, hour, minute, second, 0, 0))
    lt = utime.localtime(ts)
    weekday = lt[6]
    _rtc.datetime((year, month, day, weekday, hour, minute, second, 0))


def _parse_iso8601(datetime_str):
    """ISO 8601文字列を (year, month, day, hour, minute, second) に変換する"""
    if "T" not in datetime_str:
        raise ValueError("Invalid ISO 8601: missing 'T'")

    date_part, time_part = datetime_str.split("T", 1)
    year, month, day = map(int, date_part.split("-"))

    # タイムゾーン・小数秒を除去
    if "Z" in time_part:
        time_part = time_part.split("Z")[0]
    elif "+" in time_part:
        time_part = time_part.split("+")[0]
    elif time_part.count("-") >= 1:
        # "-06:00" 形式のタイムゾーンを除去（末尾のみ）
        idx = time_part.rfind("-")
        if idx > 2:  # HH:MM:SS の後ろのみ対象
            time_part = time_part[:idx]

    parts = time_part.split(":")
    hour = int(parts[0])
    minute = int(parts[1])
    sec_str = parts[2].split(".")[0] if len(parts) > 2 else "0"
    second = int(sec_str) if sec_str else 0

    return year, month, day, hour, minute, second
