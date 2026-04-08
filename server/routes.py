from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from . import database
from .models import SensorPayload

router = APIRouter()

# ノードごとの最新データをメモリに保持（サーバー再起動でリセット）
_latest: dict[str, dict] = {}


def _update_latest(payload: SensorPayload, *, saved_to_db: bool = False) -> None:
    prev = _latest.get(payload.node_id, {})
    _latest[payload.node_id] = {
        "node_id": payload.node_id,
        "timestamp": payload.timestamp,
        "temperature": payload.temperature,
        "humidity": payload.humidity,
        "co2": payload.co2,
        "lux": payload.lux,
        "last_seen": datetime.now(timezone.utc).isoformat(),
        # DB保存時刻：DBに書いた時だけ更新、ハートビートでは前の値を引き継ぐ
        "last_db_save": datetime.now(timezone.utc).isoformat() if saved_to_db else prev.get("last_db_save"),
    }


@router.post("/data")
def receive_data(payload: SensorPayload):
    """Pico Wからセンサデータを受信してDBに保存"""
    if payload.temperature is None:
        raise HTTPException(status_code=400, detail="temperature は必須です")

    database.insert_reading(
        node_id=payload.node_id,
        timestamp=payload.timestamp,
        temperature=payload.temperature,
        humidity=payload.humidity,
        co2=payload.co2,
        lux=payload.lux,
    )
    _update_latest(payload, saved_to_db=True)
    print(f"[INFO] 受信: {payload.model_dump()}")
    return {"status": "ok"}


@router.post("/heartbeat")
def receive_heartbeat(payload: SensorPayload):
    """Pico Wからハートビートを受信（DBには保存しない）"""
    _update_latest(payload, saved_to_db=False)
    print(f"[INFO] ハートビート: {payload.node_id} temp={payload.temperature}")
    return {"status": "ok"}


@router.get("/latest")
def get_latest():
    """全ノードの最新データ（ライブテレメトリ）"""
    return {"nodes": list(_latest.values())}


@router.get("/time")
def get_time():
    """Pi 4 の現在時刻（RTC由来）を Pico 2W に提供する"""
    return {"utc": datetime.now(timezone.utc).isoformat()}


@router.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


@router.get("/nodes")
def list_nodes():
    return {"nodes": database.query_node_ids()}


@router.get("/dates/{node_id}")
def list_dates(node_id: str):
    return {"node_id": node_id, "dates": database.query_available_dates(node_id)}


@router.get("/data/{node_id}/{date}")
def get_data(node_id: str, date: str):
    """date format: YYYY-MM-DD"""
    rows = database.query_readings(node_id, date)
    return {"node_id": node_id, "date": date, "count": len(rows), "data": rows}
