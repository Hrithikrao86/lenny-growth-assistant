# Test Plan

## Automated
Run:

```bash
docker compose exec backend pytest -q
```

Coverage includes:
- retrieval result shaping and similarity threshold forwarding;
- provider routing and invalid-provider handling;
- transcript frontmatter parsing and chunking;
- artifact envelope extraction;
- Ship 30 skill constraints;
- request validation contracts.

## Manual UI test
1. Start the stack and confirm `/api/health` reports DB and Ollama status.
2. Create a new chat and ask a transcript-grounded product question.
3. Confirm source cards appear and the answer cites episode/guest context.
4. Ask a follow-up question that depends on the previous turn.
5. Ask an unrelated/out-of-domain question and confirm the insufficient-information behavior.
6. Switch from Ollama to Claude (with an API key) and confirm the UI provider state changes.
7. Select Ship 30 mode and request an essay.
8. Request a Markdown artifact and confirm it appears in the right pane.
9. Request an HTML artifact with JavaScript and confirm it runs inside the sandboxed preview without same-origin access.
10. Stop Ollama and confirm the UI reports a useful service error rather than hanging indefinitely.
11. Restart the backend and confirm persisted session history is still available.
