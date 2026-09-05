from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, messages: list[dict[str, str]], system_prompt: str, temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        """Stream generated text chunks."""
        yield ""
