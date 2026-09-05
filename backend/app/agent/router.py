from app.config import settings
from app.providers.base import BaseLLMProvider
from app.providers.cloud_provider import ClaudeProvider
from app.providers.ollama_provider import OllamaProvider


def get_provider(name: str | None) -> BaseLLMProvider:
    selected = (name or settings.default_provider).lower()
    if selected == "ollama":
        return OllamaProvider()
    if selected == "claude":
        return ClaudeProvider()
    if selected == "claude_agent":
        from app.agent.sdk_provider import ClaudeAgentSDKProvider

        return ClaudeAgentSDKProvider()
    raise ValueError(f"Unsupported provider: {selected}")
