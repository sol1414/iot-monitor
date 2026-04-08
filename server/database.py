import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "sensor_data.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id     TEXT    NOT NULL,
                timestamp   TEXT    NOT NULL,
                temperature REAL,
                humidity    REAL,
                co2         REAL,
                lux         REAL,
                created_at  TEXT    DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_timestamp
            ON sensor_readings (node_id, timestamp)
        """)
        conn.commit()
    print(f"[INFO] DB初期化完了: {DB_PATH}")


def insert_reading(node_id: str, timestamp: str, temperature: float,
                   humidity=None, co2=None, lux=None):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO sensor_readings
                (node_id, timestamp, temperature, humidity, co2, lux)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (node_id, timestamp, temperature, humidity, co2, lux))
        conn.commit()


def query_readings(node_id: str, date: str):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT node_id, timestamp, temperature, humidity, co2, lux
            FROM sensor_readings
            WHERE node_id = ?
              AND timestamp LIKE ?
            ORDER BY timestamp ASC
        """, (node_id, f"{date}%")).fetchall()
    return [dict(row) for row in rows]


def query_node_ids():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT node_id FROM sensor_readings ORDER BY node_id"
        ).fetchall()
    return [row["node_id"] for row in rows]


def query_available_dates(node_id: str):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT DISTINCT substr(timestamp, 1, 10) AS date
            FROM sensor_readings
            WHERE node_id = ?
            ORDER BY date DESC
        """, (node_id,)).fetchall()
    return [row["date"] for row in rows]
