from pydantic import BaseModel


class SensorPayload(BaseModel):
    node_id: str
    timestamp: str
    temperature: float | None = None
    humidity: float | None = None
    co2: float | None = None
    lux: float | None = None
