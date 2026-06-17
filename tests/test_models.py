"""Tests for Pydantic model serialisation round-trips and validation."""

import pytest
from pydantic import ValidationError

from ai_client.models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ContentBlock,
)


class TestChatMessage:
    def test_roundtrip(self) -> None:
        msg = ChatMessage(role="user", content="Hello")
        assert ChatMessage.model_validate(msg.model_dump()) == msg

    def test_missing_role_raises(self) -> None:
        with pytest.raises(ValidationError):
            ChatMessage.model_validate({"content": "Hello"})

    def test_missing_content_raises(self) -> None:
        with pytest.raises(ValidationError):
            ChatMessage.model_validate({"role": "user"})


class TestChatRequest:
    def test_roundtrip_minimal(self) -> None:
        req = ChatRequest(messages=[ChatMessage(role="user", content="Hi")])
        assert ChatRequest.model_validate(req.model_dump()) == req

    def test_roundtrip_full(self) -> None:
        req = ChatRequest(
            model="claude-sonnet-latest",
            messages=[
                ChatMessage(role="user", content="Question"),
                ChatMessage(role="assistant", content="Answer"),
            ],
            max_tokens=512,
            system="You are a helpful assistant.",
        )
        assert ChatRequest.model_validate(req.model_dump()) == req

    def test_default_model(self) -> None:
        req = ChatRequest(messages=[ChatMessage(role="user", content="Hi")])
        assert req.model == "claude-sonnet-latest"

    def test_default_max_tokens(self) -> None:
        req = ChatRequest(messages=[ChatMessage(role="user", content="Hi")])
        assert req.max_tokens == 1024

    def test_empty_messages_raises(self) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(messages=[])

    def test_negative_max_tokens_raises(self) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(
                messages=[ChatMessage(role="user", content="Hi")],
                max_tokens=-1,
            )


class TestContentBlock:
    def test_roundtrip(self) -> None:
        block = ContentBlock(type="text", text="Hello world")
        assert ContentBlock.model_validate(block.model_dump()) == block

    def test_missing_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            ContentBlock.model_validate({"text": "No type"})


class TestChatResponse:
    def test_roundtrip(self) -> None:
        resp = ChatResponse(
            id="msg_abc123",
            model="claude-sonnet-latest",
            content=[ContentBlock(type="text", text="Hi there")],
            stop_reason="end_turn",
            input_tokens=10,
            output_tokens=5,
        )
        assert ChatResponse.model_validate(resp.model_dump()) == resp

    def test_defaults(self) -> None:
        resp = ChatResponse(
            id="msg_xyz",
            model="claude-sonnet-latest",
            content=[],
        )
        assert resp.stop_reason is None
        assert resp.input_tokens == 0
        assert resp.output_tokens == 0
