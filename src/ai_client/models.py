"""Pydantic v2 request/response models.

All models use ``model_config = ConfigDict(strict=True)`` to reject unexpected
fields and implicit type coercions, keeping the type boundary between the
caller and the SDK precise.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    """A single turn in a conversation."""

    model_config = ConfigDict(strict=True)

    role: str = Field(..., description="Either 'user' or 'assistant'.")
    content: str = Field(..., description="Text content of the message.")


class ChatRequest(BaseModel):
    """Parameters for a chat completion request."""

    model_config = ConfigDict(strict=True)

    model: str = Field(
        default="claude-sonnet-latest",
        description="Model identifier, e.g. 'claude-sonnet-latest'.",
    )
    messages: list[ChatMessage] = Field(
        ...,
        min_length=1,
        description="Ordered list of conversation turns.",
    )
    max_tokens: int = Field(
        default=1024,
        gt=0,
        description="Maximum number of tokens to generate.",
    )
    system: str | None = Field(
        default=None,
        description="Optional system prompt prepended to the conversation.",
    )


class ContentBlock(BaseModel):
    """A single content block returned by the API."""

    model_config = ConfigDict(strict=True)

    type: str = Field(..., description="Block type, usually 'text'.")
    text: str = Field(default="", description="Text content of this block.")


class ChatResponse(BaseModel):
    """A completed chat response."""

    model_config = ConfigDict(strict=True)

    id: str = Field(..., description="Unique response identifier.")
    model: str = Field(..., description="Model that produced this response.")
    content: list[ContentBlock] = Field(
        ...,
        description="Ordered list of content blocks.",
    )
    stop_reason: str | None = Field(
        default=None,
        description="Reason the model stopped generating.",
    )
    input_tokens: int = Field(
        default=0,
        ge=0,
        description="Number of input tokens consumed.",
    )
    output_tokens: int = Field(
        default=0,
        ge=0,
        description="Number of output tokens generated.",
    )
