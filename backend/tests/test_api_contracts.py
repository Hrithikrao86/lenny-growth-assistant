from app.models.schemas import ChatRequest, SessionCreate


def test_chat_request_validation_defaults():
    request = ChatRequest(session_id="abc", message="hello")
    assert request.mode == "default"
    assert request.provider == "ollama"


def test_session_metadata_contract():
    request = SessionCreate(title="Research", user_metadata={"source": "demo"})
    assert request.user_metadata["source"] == "demo"
