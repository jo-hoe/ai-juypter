"""Tests for AIClient.

The Anthropic SDK is mocked at the class level — ProxyConfig is constructed
directly (no os.environ side effects).
"""
from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from ai_client.client import AIClient
from ai_client.config import ProxyConfig
from ai_client.exceptions import APIError
from ai_client.models import ChatMessage, ChatRequest, ChatResponse


def _make_config() -> ProxyConfig:
    return ProxyConfig(
        auth_token="sk-test",
        base_url="http://localhost:6655/anthropic/",  # type: ignore[arg-type]
    )


def _make_sdk_message(
    *,
    text: str = "Hello from Claude",
    stop_reason: str = "end_turn",
) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text

    usage = MagicMock()
    usage.input_tokens = 10
    usage.output_tokens = 5

    msg = MagicMock()
    msg.id = "msg_test001"
    msg.model = "claude-sonnet-latest"
    msg.content = [block]
    msg.stop_reason = stop_reason
    msg.usage = usage
    return msg


def _make_request() -> ChatRequest:
    return ChatRequest(
        model="claude-sonnet-latest",
        messages=[ChatMessage(role="user", content="Hello")],
        max_tokens=256,
    )


class TestAIClientChat:
    @patch("ai_client.client.anthropic.Anthropic")
    def test_chat_returns_chat_response(self, mock_anthropic_cls: MagicMock) -> None:
        mock_sdk = mock_anthropic_cls.return_value
        mock_sdk.messages.create.return_value = _make_sdk_message()

        client = AIClient(_make_config())
        response = client.chat(_make_request())

        assert isinstance(response, ChatResponse)
        assert response.id == "msg_test001"
        assert response.stop_reason == "end_turn"
        assert len(response.content) == 1
        assert response.content[0].text == "Hello from Claude"
        assert response.input_tokens == 10
        assert response.output_tokens == 5

    @patch("ai_client.client.anthropic.Anthropic")
    def test_chat_passes_correct_params(self, mock_anthropic_cls: MagicMock) -> None:
        mock_sdk = mock_anthropic_cls.return_value
        mock_sdk.messages.create.return_value = _make_sdk_message()

        client = AIClient(_make_config())
        request = ChatRequest(
            model="claude-haiku-latest",
            messages=[ChatMessage(role="user", content="Test")],
            max_tokens=128,
            system="Be concise.",
        )
        client.chat(request)

        call_kwargs = mock_sdk.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-latest"
        assert call_kwargs["max_tokens"] == 128
        assert call_kwargs["system"] == "Be concise."
        assert len(call_kwargs["messages"]) == 1

    @patch("ai_client.client.anthropic.Anthropic")
    def test_chat_omits_system_when_none(self, mock_anthropic_cls: MagicMock) -> None:
        mock_sdk = mock_anthropic_cls.return_value
        mock_sdk.messages.create.return_value = _make_sdk_message()

        client = AIClient(_make_config())
        client.chat(ChatRequest(messages=[ChatMessage(role="user", content="Hi")]))

        call_kwargs = mock_sdk.messages.create.call_args.kwargs
        assert "system" not in call_kwargs

    @patch("ai_client.client.anthropic.Anthropic")
    def test_chat_raises_api_error_on_status_error(
        self, mock_anthropic_cls: MagicMock
    ) -> None:
        import anthropic as sdk_mod

        mock_sdk = mock_anthropic_cls.return_value
        mock_sdk.messages.create.side_effect = sdk_mod.APIStatusError(
            "Unauthorized",
            response=MagicMock(status_code=401),
            body=None,
        )

        client = AIClient(_make_config())
        with pytest.raises(APIError):
            client.chat(_make_request())

    @patch("ai_client.client.anthropic.Anthropic")
    def test_chat_raises_api_error_on_connection_error(
        self, mock_anthropic_cls: MagicMock
    ) -> None:
        import anthropic as sdk_mod

        mock_sdk = mock_anthropic_cls.return_value
        mock_sdk.messages.create.side_effect = sdk_mod.APIConnectionError(
            request=MagicMock()
        )

        client = AIClient(_make_config())
        with pytest.raises(APIError, match="Connection failed"):
            client.chat(_make_request())


class TestAIClientStreamChat:
    @patch("ai_client.client.anthropic.Anthropic")
    def test_stream_chat_yields_strings(self, mock_anthropic_cls: MagicMock) -> None:
        chunks = ["Hello", " world", "!"]

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.text_stream = iter(chunks)

        mock_sdk = mock_anthropic_cls.return_value
        mock_sdk.messages.stream.return_value = mock_stream

        client = AIClient(_make_config())
        result: list[str] = list(client.stream_chat(_make_request()))

        assert result == chunks

    @patch("ai_client.client.anthropic.Anthropic")
    def test_stream_chat_returns_iterator(
        self, mock_anthropic_cls: MagicMock
    ) -> None:
        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.text_stream = iter(["token"])

        mock_sdk = mock_anthropic_cls.return_value
        mock_sdk.messages.stream.return_value = mock_stream

        client = AIClient(_make_config())
        gen = client.stream_chat(_make_request())
        assert isinstance(gen, Iterator)
