from fastapi import APIRouter
from sqlalchemy import text
import httpx

from app.config import settings
from app.database import SessionLocal

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health():
    checks = {"db": False, "ollama": False}
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        checks["db"] = True
    except Exception:
        pass

    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            checks["ollama"] = response.is_success
    except httpx.HTTPError:
        pass

    status = "ok" if checks["db"] else "degraded"
    return {"status": status, **checks, "default_provider": settings.default_provider}
