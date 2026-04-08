from contextlib import asynccontextmanager
from fastapi import FastAPI
from . import database
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    print("[INFO] サーバー起動完了")
    yield


app = FastAPI(title="Pig Farm IoT Monitor", lifespan=lifespan)
app.include_router(router)
