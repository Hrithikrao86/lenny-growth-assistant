# Architecture

## System topology

```text
                    ┌──────────────────────────────┐
                    │        Next.js UI             │
                    │ chat · sessions · artifacts  │
                    └──────────────┬───────────────┘
                                   │ SSE / JSON
                                   ▼
                    ┌──────────────────────────────┐
                    │          FastAPI              │
                    │ API + agent routing + logs   │
                    └──────┬───────────┬───────────┘
                           │             │
                    retrieval          generation
                           │             │
                           ▼             ▼
                 ┌──────────────┐  ┌───────────────┐
                 │ PostgreSQL   │  │ Ollama /       │
                 │ + pgvector   │  │ Claude / SDK   │
                 └──────────────┘  └───────────────┘
```

## Data model

### `sessions`
- `id UUID PK`
- `title`
- `user_metadata JSONB`
- `created_at`, `updated_at`

### `messages`
- `id UUID PK`
- `session_id FK`
- `role`
- `content`
- `sources JSONB`
- `created_at`

### `artifacts`
- `id UUID PK`
- `message_id FK`
- `artifact_type` (`markdown` or `html`)
- `title`
- `content`

### `transcript_chunks`
- source path and episode metadata
- chunk index and text
- `embedding vector(768)`
- HNSW cosine index

## Ingestion
The downloader fetches the public ChatPRD Lenny transcript archive and extracts `episodes/*/transcript.md`. The repository describes each episode as YAML frontmatter followed by the full transcript.

The ingestion pipeline:

```text
archive → YAML parser → ~650-token chunks / ~100 overlap
        → Ollama nomic-embed-text
        → PostgreSQL vector(768)
        → HNSW cosine index
```

Re-running ingestion deletes the existing chunks for each source path before inserting the refreshed chunks, making the operation idempotent.

## Retrieval
1. Build a retrieval query from the current question plus the last two user turns.
2. Generate an embedding.
3. Run cosine similarity search.
4. Return up to `RETRIEVAL_TOP_K` chunks above `SIMILARITY_THRESHOLD`.
5. Format the returned chunks into explicit source blocks.
6. If no chunks pass the threshold, stop generation.

## Agent and provider boundaries
- `BaseLLMProvider`: streaming interface.
- `OllamaProvider`: mandatory local demo path.
- `ClaudeProvider`: direct cloud API path.
- `ClaudeAgentSDKProvider`: optional agent-runtime adapter using Anthropic's Claude Agent SDK.
- `agent/prompts.py`: grounding and Ship 30 skill policy.
- `skills/artifact_generator.py`: artifact envelope parsing.

The application can change provider through the API request without changing core retrieval or UI code.

## API

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/sessions` | Create independent session |
| GET | `/api/sessions` | List recent sessions |
| GET | `/api/sessions/{id}` | Load history |
| POST | `/api/chat` | Stream grounded answer |
| GET | `/api/health` | DB/Ollama readiness |

`POST /api/chat` emits SSE events of type `status`, `sources`, `token`, `artifact`, `error`, then `[DONE]`.

## Security
HTML artifacts are untrusted. The browser sanitizes the HTML with DOMPurify before assigning it to `srcDoc`. The iframe uses `sandbox="allow-scripts"` and does **not** grant `allow-same-origin`, `allow-forms`, or popup permissions. This allows interactive client-side demos while isolating the document from the application's origin.

## Deployment topology
Docker Compose runs:
- `db`: PostgreSQL 16 + pgvector.
- `backend`: FastAPI.
- `frontend`: Next.js.

Ollama is intentionally external to Compose by default because the assignment requires a local model demo and Ollama is commonly installed on the host. `host.docker.internal` bridges the backend container to Ollama on Windows/macOS Docker Desktop.
