# AI-assisted engineering log 03 — security and handoff

## Artifact threat model
Generated HTML is treated as untrusted. The browser viewer uses DOMPurify and a sandboxed iframe with `sandbox="allow-scripts"` and deliberately omits `allow-same-origin`.

## Why scripts are still permitted
The assignment asks for interactive HTML/CSS artifacts. `allow-scripts` permits client-side interactivity, while the missing `allow-same-origin` keeps the document in an opaque origin so it cannot use the parent application's origin-bound cookies, storage, or DOM.

## Handoff improvements
- Added `/api/health` checks for database and Ollama.
- Added structured application logging.
- Added explicit provider errors for missing API keys and unavailable services.
- Added `.env.example` and `.gitignore`.
- Added unit tests for retrieval, provider routing, ingestion, artifact parsing, and request contracts.
