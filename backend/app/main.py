import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    stream=sys.stdout,
)

app = FastAPI(title="The Lenny Growth Assistant", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    await init_db()


@app.get("/")
async def root():
    return {"name": "The Lenny Growth Assistant", "status": "running"}


app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(health_router)
