from collections.abc import Sequence

import httpx

from app.config import settings


async def embed(text: str) -> list[float]:
    """Generate embeddings through Ollama so the backend does not need PyTorch/CUDA."""
    if not text.strip():
        raise ValueError("Cannot embed empty text")

    payload = {"model": settings.ollama_embedding_model, "input": text}
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{settings.ollama_base_url}/api/embed", json=payload)
        response.raise_for_status()
        data = response.json()

    embeddings: Sequence[Sequence[float]] = data.get("embeddings", [])
    if not embeddings:
        raise RuntimeError("Ollama returned no embedding")
    return list(embeddings[0])
