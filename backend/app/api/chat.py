import json
import logging
import re
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.agent.prompts import GROUNDED_SYSTEM
from app.agent.router import get_provider
from app.config import settings
from app.database import SessionLocal
from app.models.db_models import Artifact, Message, Session
from app.models.schemas import ChatRequest
from app.rag.embeddings import embed
from app.rag.retriever import TranscriptRetriever
from app.skills.artifact_generator import extract_artifact, strip_artifact
from app.skills.ship30_writer import build_ship30_prompt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


def source_label(item: dict) -> dict:
    return {
        "episode": item["episode"],
        "guest": item["guest"],
        "timestamp": item.get("timestamp"),
        "score": round(item["score"], 3),
        "source_path": item.get("source_path"),
    }


def format_context(items: list[dict]) -> str:
    if not items:
        return "NO SUPPORTING TRANSCRIPT CONTEXT WAS RETRIEVED."
    blocks = []
    for i, item in enumerate(items, 1):
        ref = f"[Episode: {item['episode']}, {item.get('timestamp') or 'topic context'}]"
        blocks.append(
            f"SOURCE {i} {ref} (guest: {item['guest']}, similarity: {item['score']:.3f})\n{item['text']}"
        )
    return "\n\n".join(blocks)


@router.post("")
async def chat(req: ChatRequest):
    try:
        session_id = uuid.UUID(req.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid session_id") from exc

    async def event_stream() -> AsyncGenerator[str, None]:
        async with SessionLocal() as db:
            session = await db.get(Session, session_id)
            if not session:
                yield "data: " + json.dumps({"type": "error", "content": "Session not found"}) + "\n\n"
                return

            user_message = Message(session_id=session_id, role="user", content=req.message, sources=[])
            db.add(user_message)
            await db.flush()

            history_result = await db.execute(
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(Message.created_at.desc())
                .limit(settings.max_history_messages)
            )
            previous = list(reversed(history_result.scalars().all()))[:-1]
            history = [{"role": m.role, "content": m.content} for m in previous]

            yield "data: " + json.dumps({"type": "status", "content": "Retrieving transcripts…"}) + "\n\n"
            retrieval_query = "\n".join(m["content"] for m in history[-2:] if m["role"] == "user")
            retrieval_query = f"{retrieval_query}\n{req.message}".strip()

            try:
                retriever = TranscriptRetriever(db, embed)
                chunks = await retriever.retrieve_relevant_chunks(retrieval_query)
            except Exception as exc:
                logger.exception("retrieval_failed", extra={"session_id": str(session_id)})
                await db.rollback()
                yield "data: " + json.dumps(
                    {"type": "error", "content": "Knowledge retrieval is unavailable. Check Ollama and the embedding model."}
                ) + "\n\n"
                return

            sources = [source_label(item) for item in chunks]
            yield "data: " + json.dumps({"type": "sources", "sources": sources}) + "\n\n"

            if not chunks:
    if req.provider == "claude":
        system_prompt = (
            "You are Lenny's Growth Assistant. "
            "Answer the user's question using your knowledge only when it is "
            "directly relevant to product, growth, startups, or leadership. "
            "Be concise and useful. Clearly state when the answer is not "
            "supported by the available podcast archive."
        )

        provider = get_provider(req.provider)
        yield "data: " + json.dumps(
            {"type": "status", "content": "Generating with Claude…"}
        ) + "\n\n"

        full_response = ""
        try:
            async for token in provider.generate_response(
                history + [{"role": "user", "content": req.message}],
                system_prompt,
            ):
                full_response += token
                yield "data: " + json.dumps(
                    {"type": "token", "content": token}
                ) + "\n\n"

            assistant_message = Message(
                session_id=session_id,
                role="assistant",
                content=full_response,
                sources=[],
            )
            db.add(assistant_message)
            await db.commit()
            yield "data: [DONE]\n\n"
            return

        except Exception as exc:
            logger.exception("llm_failed", extra={"provider": req.provider})
            await db.rollback()
            yield "data: " + json.dumps(
                {"type": "error", "content": f"Claude is unavailable: {exc}"}
            ) + "\n\n"
            return

    answer = "I do not have sufficient information in Lenny's podcast archive to answer this."
    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=answer,
        sources=[],
    )
    db.add(assistant_message)
    await db.commit()
    yield "data: " + json.dumps({"type": "token", "content": answer}) + "\n\n"
    yield "data: [DONE]\n\n"
    return

            context = format_context(chunks)
            if req.mode == "ship30":
                system_prompt = build_ship30_prompt(chunks, req.message)
            else:
                system_prompt = GROUNDED_SYSTEM.format(context=context)

            messages = history + [{"role": "user", "content": req.message}]
            provider = get_provider(req.provider)
            yield "data: " + json.dumps(
                {"type": "status", "content": f"Generating with {req.provider}…"}
            ) + "\n\n"

            full_response = ""
            try:
                async for token in provider.generate_response(messages, system_prompt):
                    full_response += token
                    yield "data: " + json.dumps({"type": "token", "content": token}) + "\n\n"
            except Exception as exc:
                logger.exception("llm_failed", extra={"provider": req.provider, "session_id": str(session_id)})
                await db.rollback()
                yield "data: " + json.dumps(
                    {"type": "error", "content": f"{req.provider} is unavailable: {exc}"}
                ) + "\n\n"
                return

            artifact = extract_artifact(full_response)
            clean_response = strip_artifact(full_response) if artifact else full_response
            if artifact:
                yield "data: " + json.dumps(
                    {"type": "artifact", "artifact": artifact}
                ) + "\n\n"

            assistant_message = Message(
                session_id=session_id,
                role="assistant",
                content=clean_response,
                sources=sources,
            )
            db.add(assistant_message)
            await db.flush()
            if artifact:
                db.add(
                    Artifact(
                        message_id=assistant_message.id,
                        artifact_type=artifact["artifact_type"],
                        title=artifact["title"],
                        content=artifact["content"],
                    )
                )
            if session.title == "New session":
                session.title = re.sub(r"\s+", " ", req.message).strip()[:60] or "New session"
            await db.commit()
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
