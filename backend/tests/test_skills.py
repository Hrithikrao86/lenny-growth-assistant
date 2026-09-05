from app.agent.prompts import SHIP30_SYSTEM
from app.skills.artifact_generator import extract_artifact, strip_artifact
from app.skills.ship30_writer import build_ship30_prompt


def test_artifact_extraction():
    raw = 'Before <artifact type="html" title="Growth Loop"> <h1>Hello</h1> </artifact> after'
    artifact = extract_artifact(raw)
    assert artifact["artifact_type"] == "html"
    assert artifact["title"] == "Growth Loop"
    assert "Hello" in artifact["content"]
    assert strip_artifact(raw) == "Before  after"


def test_ship30_prompt_has_structural_constraints():
    prompt = build_ship30_prompt(
        [{"episode": "E", "guest": "G", "timestamp": "10:00", "text": "Insight"}],
        "Write about this",
    )
    assert "approximately 1,250-word essay" in prompt
    assert "specific operational takeaway" in prompt
    assert "Episode: E" in prompt
