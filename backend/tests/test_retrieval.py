import pytest

from app.rag.retriever import TranscriptRetriever


class FakeResult:
    def fetchall(self):
        class Row:
            episode_title = "Episode A"
            guest_name = "Guest A"
            publish_date = "2026-01-01"
            chunk_text = "A useful growth lesson."
            timestamp_ref = "12:34"
            source_path = "data/transcripts/guest/transcript.md"
            chunk_index = 2
            similarity_score = 0.81

        return [Row()]


class FakeSession:
    async def execute(self, stmt, params):
        assert params["threshold"] == 0.6
        assert params["limit"] == 3
        return FakeResult()


@pytest.mark.asyncio
async def test_retriever_returns_ranked_source_metadata():
    async def embedding_fn(_: str):
        return [0.1, 0.2]

    retriever = TranscriptRetriever(FakeSession(), embedding_fn)
    rows = await retriever.retrieve_relevant_chunks("growth", top_k=3, similarity_threshold=0.6)
    assert rows[0]["episode"] == "Episode A"
    assert rows[0]["timestamp"] == "12:34"
    assert rows[0]["score"] == 0.81
