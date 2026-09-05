# Product Requirements — The Lenny Growth Assistant

## 1. Discovery brief

### User and problem
**Primary user:** a product or growth PM who needs an actionable answer without listening through hundreds of hours of podcast audio.

**Job to be done:** ask a product/growth question, get a concise answer grounded in Lenny's Podcast transcripts, inspect the sources, and optionally turn the answer into reusable written content or an artifact.

**Pain removed:** slow information retrieval, uncertain attribution, and repetitive conversion of research into publishable or shareable formats.

### Success metrics
- **Citation accuracy:** ≥90% of evaluated substantive claims are supported by a retrieved transcript source.
- **Local responsiveness:** <4 seconds to first token on a representative local Ollama setup after retrieval.
- **Artifact safety:** 0 known XSS escape paths in the viewer's security test suite.
- **Operational recovery:** service health endpoint identifies DB/Ollama degradation without requiring log inspection first.

## 2. Assumptions
1. The transcript archive is the source of truth for substantive answers.
2. The evaluator can run Ollama locally and has enough RAM/CPU for the selected model.
3. A cloud API key is optional; the mandatory demo path is local Ollama.
4. Anonymous local sessions are sufficient for the take-home; enterprise authentication/SSO is intentionally out of scope.
5. Transcript refresh is an operator command rather than a scheduled production pipeline.

## 3. Scope
### Included
- Grounded conversational RAG over Lenny transcripts.
- Independent PostgreSQL-backed sessions and message history.
- Local Ollama and cloud Claude provider selection.
- Optional Claude Agent SDK adapter for the agent layer.
- Ship 30 for 30 writing skill.
- Markdown and HTML artifact generation and in-app preview.
- Docker Compose startup, health checks, structured logs, tests, and handoff docs.

### Intentionally excluded
- User authentication and multi-tenant authorization.
- Production cloud deployment.
- Automatic transcript crawling on a schedule.
- Audio transcription itself; the assignment provides a transcript repository.
- Web search or external knowledge during grounded QA.

These exclusions keep the demo focused on the evaluation criteria: grounding, agent architecture, operability, and product judgment.

## 4. Core flows

### Grounded question
1. User starts/selects a session.
2. User submits a product/growth question.
3. Backend persists the message.
4. Recent conversation context is combined with the current query for retrieval.
5. Query embedding is generated through Ollama.
6. pgvector returns top-K chunks above the similarity threshold.
7. If no chunks qualify, the system returns the required insufficient-information response.
8. Otherwise, the provider receives only the conversation plus retrieved transcript context.
9. Response streams to the UI with source metadata.
10. Assistant response and source list are persisted.

### Ship 30 for 30
The same retrieval path is used, but the dedicated skill prompt imposes the writing system: strong hook, clear organizing framework, short paragraphs, skimmable formatting, clear language, and a concrete takeaway. Claims remain grounded in retrieved sources.

### Artifact
The assistant can emit an `<artifact>` envelope. The backend extracts and persists it, then the UI renders Markdown natively or HTML inside a sandboxed iframe.

## 5. Acceptance criteria
- A new session receives a unique ID and maintains independent history.
- A follow-up question can use recent session context during retrieval and generation.
- Unsupported questions return the exact insufficient-information behavior without hallucinated content.
- Every grounded answer exposes the retrieved source metadata.
- Provider selection is visible and does not require application code changes.
- Ship 30 mode produces approximately 1,250 words when sufficient context exists.
- HTML artifacts cannot access the parent origin because `allow-same-origin` is omitted.
- Missing API keys, unavailable Ollama, failed retrieval, and DB failures produce actionable errors.
- `docker compose up --build` is the primary startup path.

## 6. Risks and trade-offs
| Risk | Mitigation / decision |
|---|---|
| Hallucination | Retrieval threshold + no-context hard stop + source citations. |
| Local model quality | Use a small Ollama model for the required demo; expose Claude as an optional higher-quality path. |
| Latency | Keep retrieval top-K small and stream generation. |
| Cost | Local default; cloud is optional. |
| Data leakage | No external search in grounded mode; cloud use is explicit. |
| Unsafe HTML | DOMPurify + sandboxed iframe with no same-origin permission. |
| Transcript drift | Source path, episode metadata, chunk index, and an explicit re-ingestion command provide traceability. |

## 7. Implementation plan
1. Ingest the public transcript archive.
2. Generate embeddings and HNSW index.
3. Implement retrieval and grounded prompts.
4. Add provider/agent routing.
5. Add persistence and streaming API.
6. Add artifact generation/viewer.
7. Add resilience, tests, documentation, and demo workflow.
