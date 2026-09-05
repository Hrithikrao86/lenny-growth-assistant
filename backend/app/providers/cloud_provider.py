from collections.abc import AsyncGenerator

from app.config import settings
from app.providers.base import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    async def generate_response(
        self, messages: list[dict[str, str]], system_prompt: str, temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")

        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        async with client.messages.stream(
            model=settings.anthropic_model,
            max_tokens=3000,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
        ) as stream:
            async for text in stream.text_stream:
                yield text
