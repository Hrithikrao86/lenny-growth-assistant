from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True, pool_recycle=1800)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    async with engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Import models before create_all so SQLAlchemy sees every table.
        from app.models import db_models  # noqa: F401

        await connection.run_sync(Base.metadata.create_all)
        await connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_transcript_chunks_embedding_hnsw "
                "ON transcript_chunks USING hnsw (embedding vector_cosine_ops)"
            )
        )
