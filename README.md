# The Lenny Growth Assistant

A forward-deployed, transcript-grounded AI workspace for product and growth teams. It combines PostgreSQL/pgvector RAG, local Ollama inference, optional Claude, a dedicated Ship 30 for 30 writing skill, and an in-app artifact viewer.

## 1. Prerequisites

- Windows + Docker Desktop with WSL2, macOS, or Linux.
- Docker Compose.
- Ollama installed and running on the host for the mandatory local demo.
- Recommended local models:
  - `llama3.2:3b`
  - `nomic-embed-text`

The transcript source is the public ChatPRD Lenny transcript repository: https://github.com/ChatPRD/lennys-podcast-transcripts

## 2. Quick start

```powershell
copy .env.example .env

docker compose up --build
```

In another PowerShell window, prepare Ollama:

```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Open http://localhost:3000.

## 3. Load the knowledge base

After the containers are running:

```powershell
docker compose exec backend python scripts/download_transcripts.py
docker compose exec backend python scripts/ingest.py
```

The downloader stores transcripts under `data/transcripts`. This directory is ignored by Git because it is generated data.

## 4. Environment variables

See `.env.example` for all variables.

| Variable | Required | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | local demo | Ollama endpoint; Docker Desktop default uses `host.docker.internal`. |
| `OLLAMA_MODEL` | local demo | Local generation model. |
| `OLLAMA_EMBEDDING_MODEL` | local demo | Embedding model. |
| `ANTHROPIC_API_KEY` | cloud only | Claude API key. |
| `ANTHROPIC_MODEL` | cloud only | Claude model identifier. |
| `DEFAULT_PROVIDER` | no | `ollama`, `claude`, or `claude_agent`. |
| `SIMILARITY_THRESHOLD` | no | Retrieval cutoff. |
| `RETRIEVAL_TOP_K` | no | Maximum chunks returned. |

Never commit `.env` or API keys.

## 5. Provider behavior

- **Ollama:** mandatory demo path; backend reaches the host Ollama instance through Docker Desktop networking.
- **Claude:** optional cloud path through the Anthropic Python SDK.
- **Claude Agent SDK:** optional agent-runtime path. It is included to satisfy the assignment's agent-layer requirement while preserving Ollama as the deterministic local demo path.

## 6. Grounding behavior

The assistant never asks the model to answer from general world knowledge in grounded mode. It retrieves transcript chunks first. If no chunk exceeds the configured threshold, it returns:

> I do not have sufficient information in Lenny's podcast archive to answer this.

Successful answers persist the retrieved source metadata with the assistant message.

## 7. Artifacts

Ask for a Markdown or HTML artifact in the conversation. The model emits an artifact envelope that the backend extracts and persists.

- Markdown → `react-markdown` + GFM.
- HTML → DOMPurify + `iframe srcDoc`.
- iframe sandbox → `sandbox="allow-scripts"`, with no `allow-same-origin`.

This is a defense-in-depth boundary for generated, untrusted HTML.

## 8. Tests

```powershell
docker compose exec backend pytest -q
```

See `docs/test-plan.md` for the manual UI plan.

## 9. Troubleshooting

### `docker` is not recognized
Install Docker Desktop, restart Windows, open Docker Desktop, then open a new PowerShell window and verify:

```powershell
docker --version
docker compose version
```

### Ollama unavailable
Confirm Ollama is running:

```powershell
ollama list
```

Then confirm both models exist:

```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### No transcript sources
Run the downloader and ingestion commands from section 3. Then retry the question.

### Backend is slow to build
The backend intentionally uses Ollama for embeddings instead of installing Sentence Transformers/PyTorch. This avoids a large CUDA dependency tree in the API container.

### Cloud provider says API key is missing
Set `ANTHROPIC_API_KEY` in `.env`, then restart:

```powershell
docker compose up --build
```

## 10. Project structure

```text
lenny-growth-assistant/
├── .env.example
├── docker-compose.yml
├── README.md
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   ├── design.md
│   └── test-plan.md
├── agent_transcripts/
├── data/transcripts/           # generated, gitignored
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   ├── api/
│   │   ├── models/
│   │   ├── providers/
│   │   ├── rag/
│   │   └── skills/
│   ├── scripts/
│   └── tests/
└── frontend/
    └── src/
```

## 11. Handoff checklist

- `docker compose up --build` starts the product.
- Ollama models are documented and selected visibly in the UI.
- Transcript download and ingestion are explicit and repeatable.
- RAG has a hard no-context failure mode.
- Sessions and messages persist in PostgreSQL.
- Health checks expose DB/Ollama readiness.
- Generated HTML is isolated from the application origin.
- AI-assisted engineering logs document failures and corrections.
- Automated and manual test plans are included.

## 12. Demo narrative

For the required 2–3 minute demo:
1. Introduce the PM/growth research problem.
2. Ask one grounded question and show sources.
3. Ask a follow-up to demonstrate session context.
4. Switch/confirm Ollama and explain the local/cloud trade-off.
5. Generate a short artifact and show the sandboxed preview.
6. Close with one architectural decision: Ollama handles both local generation and embeddings so the backend remains lightweight and the demo has no cloud dependency.
