# AI-assisted engineering log 01 — initial scaffold

## Goal
Translate the Oogway Labs brief into a runnable FastAPI + PostgreSQL + Next.js application.

## Initial approach
- FastAPI API and SQLAlchemy persistence.
- Ollama and Claude provider abstraction.
- Sentence Transformers for embeddings.
- Next.js dual-pane chat/artifact UI.

## Verification
- Frontend production build completed.
- Backend dependency installation completed.
- Docker Compose reached backend image export.

## Problem discovered
The embedding dependency pulled a CUDA-enabled PyTorch stack into the backend image. The build log showed a 554.6 MB Torch wheel plus several large NVIDIA libraries.

## Decision
Replace local Sentence Transformers runtime with Ollama's `nomic-embed-text` endpoint. This keeps local inference responsibility in Ollama, removes unnecessary CUDA/PyTorch weight from the backend, and remains within the assignment's allowed embedding choices.
