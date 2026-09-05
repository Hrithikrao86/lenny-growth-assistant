# AI-assisted engineering log 02 — RAG integration correction

## Initial implementation gap
The first chat endpoint displayed a “Retrieving transcripts…” status but did not actually call the retriever before invoking the LLM.

## Correction
The final implementation now:
1. Validates the session.
2. Persists the incoming user message.
3. Builds a retrieval query using the current question and recent user context.
4. Embeds the query with Ollama.
5. Retrieves top-K transcript chunks from PostgreSQL/pgvector using cosine similarity.
6. Stops before generation when no chunk passes the threshold.
7. Adds source metadata to the streamed response and persisted assistant message.
8. Builds a grounded system prompt containing only retrieved transcript context.

## Grounding behavior
If retrieval returns no supporting chunks, the assistant returns the required insufficient-information message instead of asking the LLM to guess.
