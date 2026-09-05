from app.skills.artifact_generator import extract_artifact
from app.rag.parser import chunk_text, parse_transcript


def test_chunking_preserves_timestamp_reference():
    text = "[01:23] " + "word " * 900
    chunks = chunk_text(text, target_tokens=650, overlap_tokens=100)
    assert len(chunks) >= 2
    assert chunks[0][1] == "01:23"


def test_frontmatter_parser(tmp_path):
    path = tmp_path / "transcript.md"
    path.write_text("---\nguest: Jane\ntitle: Test Episode\npublish_date: 2026-01-01\n---\nHello transcript", encoding="utf-8")
    metadata, body = parse_transcript(str(path))
    assert metadata["guest"] == "Jane"
    assert metadata["title"] == "Test Episode"
    assert body == "Hello transcript"
