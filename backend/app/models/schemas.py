from typing import Literal

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    title: str = Field(default="New session", min_length=1, max_length=255)
    user_metadata: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=10000)
    mode: Literal["default", "ship30"] = "default"
    provider: Literal["ollama", "claude", "claude_agent"] = "ollama"


class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
