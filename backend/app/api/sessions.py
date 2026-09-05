import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import SessionLocal
from app.models.db_models import Message, Session
from app.models.schemas import SessionCreate

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("")
async def create_session(req: SessionCreate | None = None):
    req = req or SessionCreate()
    async with SessionLocal() as db:
        session = Session(title=req.title, user_metadata=req.user_metadata)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return {"id": str(session.id), "title": session.title}


@router.get("")
async def list_sessions():
    async with SessionLocal() as db:
        result = await db.execute(select(Session).order_by(Session.updated_at.desc()).limit(50))
        return [
            {"id": str(item.id), "title": item.title, "updated_at": item.updated_at.isoformat()}
            for item in result.scalars().all()
        ]


@router.get("/{session_id}")
async def history(session_id: str):
    try:
        parsed_id = uuid.UUID(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid session_id") from exc

    async with SessionLocal() as db:
        session = await db.get(Session, parsed_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        result = await db.execute(
            select(Message).where(Message.session_id == parsed_id).order_by(Message.created_at.asc())
        )
        return {
            "id": str(session.id),
            "title": session.title,
            "messages": [
                {"id": str(m.id), "role": m.role, "content": m.content, "sources": m.sources}
                for m in result.scalars().all()
            ],
        }
