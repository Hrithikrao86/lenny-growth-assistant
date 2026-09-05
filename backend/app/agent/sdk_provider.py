"""Optional Claude Agent SDK adapter required by the assignment's agent-layer contract."""

from collections.abc import AsyncGenerator

from app.providers.base import BaseLLMProvider


class ClaudeAgentSDKProvider(BaseLLMProvider):
    async def generate_response(
        self, messages: list[dict[str, str]], system_prompt: str, temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        try:
            from claude_agent_sdk import AssistantMessage, TextBlock, query
        except ImportError as exc:
            raise RuntimeError("claude-agent-sdk is not installed") from exc

        transcript = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        prompt = f"{system_prompt}\n\nConversation:\n{transcript}"
        async for message in query(prompt=prompt):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        yield block.text
