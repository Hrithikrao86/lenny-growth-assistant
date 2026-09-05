import re
from pathlib import Path

import yaml

TIMESTAMP_RE = re.compile(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]")


def parse_transcript(path: str) -> tuple[dict, str]:
    raw = Path(path).read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, flags=re.DOTALL)
    if not match:
        return {}, raw
    metadata = yaml.safe_load(match.group(1)) or {}
    return metadata, match.group(2).strip()


def chunk_text(text: str, target_tokens: int = 650, overlap_tokens: int = 100) -> list[tuple[str, str | None]]:
    words = text.split()
    if not words:
        return []
    step = max(1, target_tokens - overlap_tokens)
    chunks: list[tuple[str, str | None]] = []
    for start in range(0, len(words), step):
        part = " ".join(words[start : start + target_tokens]).strip()
        if not part:
            continue
        timestamps = TIMESTAMP_RE.findall(part)
        chunks.append((part, timestamps[0] if timestamps else None))
        if start + target_tokens >= len(words):
            break
    return chunks
