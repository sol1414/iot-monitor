# =============================================================
# test_server.py - サーバー動作確認テスト
# PC上で実行可能（Pi 4 不要）
# 実行: python server/tests/test_server.py
# =============================================================

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import database
import random
from datetime import datetime, timedelta

# テスト用DBをオーバーライド
database.DB_PATH = Path(__file__).parent / "test_data.db"


def setup():
    """テスト用DB初期化"""
    if database.DB_PATH.exists():
        database.DB_PATH.unlink()
    database.init_db()
    print("[SETUP] テスト用DB初期化完了")


def insert_mock_data():
    """モックデータを挿入（node01, 今日の1日分）"""
    today = datetime.now().strftime("%Y-%m-%d")
    base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    count = 0
    for i in range(288):  # 5分×288 = 24時間
        ts = base_time + timedelta(minutes=5 * i)
        hour = ts.hour
        base_temp = 20.0 + 5.0 * abs(hour - 12) / 12 * (-1) + 5.0
        temp = round(base_temp + random.uniform(-1.0, 1.0), 2)

        database.insert_reading(
            node_id="node01",
            timestamp=ts.strftime("%Y-%m-%dT%H:%M:%S+09:00"),
            temperature=temp,
        )
        count += 1

    print(f"[MOCK] {count}件のモックデータを挿入 (node01, {today})")
    return today


def test_query():
    """データ取得テスト"""
    today = datetime.now().strftime("%Y-%m-%d")
    rows = database.query_readings("node01", today)
    assert len(rows) > 0, "データが取得できません"
    assert "temperature" in rows[0], "temperatureカラムが存在しません"
    print(f"[TEST] query_readings: OK ({len(rows)}件取得)")


def test_node_ids():
    """ノードID一覧取得テスト"""
    nodes = database.query_node_ids()
    assert "node01" in nodes
    print(f"[TEST] query_node_ids: OK {nodes}")


def test_available_dates():
    """日付一覧取得テスト"""
    dates = database.query_available_dates("node01")
    assert len(dates) > 0
    print(f"[TEST] query_available_dates: OK {dates}")


def test_fastapi_import():
    """FastAPIモジュールのインポートテスト"""
    import server.main  # noqa
    print("[TEST] FastAPIモジュールのインポート: OK")


def run_all():
    setup()
    insert_mock_data()
    test_query()
    test_node_ids()
    test_available_dates()
    test_fastapi_import()

    print()
    print("=" * 40)
    print("全テスト通過")
    print(f"テスト用DB: {database.DB_PATH}")
    print("ダッシュボード確認用コマンド:")
    print("  cd client && streamlit run app.py")
    print("=" * 40)


if __name__ == "__main__":
    run_all()
