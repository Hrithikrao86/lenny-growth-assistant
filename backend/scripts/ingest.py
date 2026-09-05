"""Parse, chunk, embed, and index Lenny transcript Markdown files."""

import asyncio
import glob
import os
from pathlib import Path

from sqlalchemy import delete

from app.database import SessionLocal, init_db
from app.models.db_models import TranscriptChunk
from app.rag.embeddings import embed
from app.rag.parser import chunk_text, parse_transcript


async def ingest() -> None:
    await init_db()
    pattern = os.getenv("TRANSCRIPT_GLOB", "data/transcripts/**/transcript.md")
    paths = sorted(glob.glob(pattern, recursive=True))
    if not paths:
        raise SystemExit(
            "No transcripts found. Run: python scripts/download_transcripts.py"
        )

    async with SessionLocal() as db:
        indexed = 0
        for path in paths:
            metadata, body = parse_transcript(path)
            guest = metadata.get("guest") or Path(path).parent.name.replace("-", " ").title()
            title = metadata.get("title") or Path(path).parent.name
            publish_date = str(metadata.get("publish_date") or "")

            # Idempotency: replace chunks for the source file on re-ingestion.
            await db.execute(delete(TranscriptChunk).where(TranscriptChunk.source_path == path))
            for index, (chunk, timestamp) in enumerate(chunk_text(body)):
                vector = await embed(chunk)
                db.add(
                    TranscriptChunk(
                        source_path=path,
                        episode_title=title,
                        guest_name=guest,
                        publish_date=publish_date,
                        timestamp_ref=timestamp,
                        chunk_index=index,
                        chunk_text=chunk,
                        embedding=vector,
                    )
                )
                indexed += 1
            await db.commit()
            print(f"Indexed {path}")

    print(f"Done. Indexed {indexed} transcript chunks from {len(paths)} episodes.")


if __name__ == "__main__":
    asyncio.run(ingest())
