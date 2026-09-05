from collections.abc import Callable, Awaitable
from typing import Any

from sqlalchemy import text

from app.config import settings


class TranscriptRetriever:
    def __init__(self, session: Any, embedding_fn: Callable[[str], Awaitable[list[float]]]):
        self.session = session
        self.embedding_fn = embedding_fn

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        top_k = top_k or settings.retrieval_top_k
        threshold = settings.similarity_threshold if similarity_threshold is None else similarity_threshold

        # Preferred path: semantic retrieval with Ollama embeddings.
        try:
            query_vector = await self.embedding_fn(query)

            stmt = text(
                """
                SELECT episode_title, guest_name, publish_date, chunk_text, timestamp_ref,
                       source_path, chunk_index,
                       1 - (embedding <=> CAST(:vector AS vector)) AS similarity_score
                FROM transcript_chunks
                WHERE 1 - (embedding <=> CAST(:vector AS vector)) >= :threshold
                ORDER BY embedding <=> CAST(:vector AS vector)
                LIMIT :limit
                """
            )

            result = await self.session.execute(
                stmt,
                {
                    "vector": str(query_vector),
                    "threshold": threshold,
                    "limit": top_k,
                },
            )

            rows = result.fetchall()

            if rows:
                return [
                    {
                        "episode": row.episode_title,
                        "guest": row.guest_name,
                        "publish_date": row.publish_date,
                        "text": row.chunk_text,
                        "timestamp": row.timestamp_ref,
                        "source_path": row.source_path,
                        "chunk_index": row.chunk_index,
                        "score": float(row.similarity_score),
                    }
                    for row in rows
                ]

        except Exception:
            # Cloud deployment may not have access to the local Ollama service.
            pass

        # Fallback: PostgreSQL full-text retrieval.
        fallback_stmt = text(
            """
            SELECT episode_title, guest_name, publish_date, chunk_text, timestamp_ref,
                   source_path, chunk_index,
                   ts_rank(
                       to_tsvector('english', chunk_text),
                       websearch_to_tsquery('english', :query)
                   ) AS similarity_score
            FROM transcript_chunks
            WHERE to_tsvector('english', chunk_text)
                  @@ websearch_to_tsquery('english', :query)
            ORDER BY similarity_score DESC
            LIMIT :limit
            """
        )

        result = await self.session.execute(
            fallback_stmt,
            {
                "query": query,
                "limit": top_k,
            },
        )

        return [
            {
                "episode": row.episode_title,
                "guest": row.guest_name,
                "publish_date": row.publish_date,
                "text": row.chunk_text,
                "timestamp": row.timestamp_ref,
                "source_path": row.source_path,
                "chunk_index": row.chunk_index,
                "score": float(row.similarity_score),
            }
            for row in result.fetchall()
        ]