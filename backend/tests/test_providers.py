import pytest

from app.agent.router import get_provider
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import ClaudeProvider


def test_provider_routing():
    assert isinstance(get_provider("ollama"), OllamaProvider)
    assert isinstance(get_provider("claude"), ClaudeProvider)


def test_invalid_provider():
    with pytest.raises(ValueError):
        get_provider("unknown")
