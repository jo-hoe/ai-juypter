"""AIClient — thin, strongly-typed wrapper around the Anthropic Python SDK.

Design constraints:
- No global state.
- No raw httpx calls; the Anthropic SDK handles transport.
- ``chat`` returns a fully-deserialised ``ChatResponse``.
- ``stream_chat`` yields ``str`` deltas using the SDK's ``text_stream``.
- All SDK errors are mapped to package-local ``APIError``.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Literal, cast

import anthropic

from .config import ProxyConfig
from .exceptions import APIError
from .models import ChatMessage, ChatRequest, ChatResponse, ContentBlock

_VALID_ROLES = frozenset({"user", "assistant"})


def _build_sdk_messages(
    messages: list[ChatMessage],
) -> list[anthropic.types.MessageParam]:
    """Convert ``ChatMessage`` objects to the SDK's wire format."""
    return [
        anthropic.types.MessageParam(
            role=cast(Literal["user", "assistant"], msg.role),
            content=msg.content,
        )
        for msg in messages
    ]


class AIClient:
    """Sends requests to the Anthropic API through an optional proxy.

    The client is stateless after construction — every method creates a fresh
    SDK ``Message`` and returns without mutating internal state.
    """

    def __init__(self, config: ProxyConfig) -> None:
        self._config = config
        self._sdk = anthropic.Anthropic(
            api_key=config.auth_token,
            base_url=config.base_url_str,
        )

    def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a blocking chat request and return a ``ChatResponse``.

        Args:
            request: The fully-specified chat request.

        Returns:
            A ``ChatResponse`` with content blocks and usage stats.

        Raises:
            APIError: When the upstream API returns an error.
        """
        try:
            if request.system is not None:
                sdk_response = self._sdk.messages.create(
                    model=request.model,
                    max_tokens=request.max_tokens,
                    messages=_build_sdk_messages(request.messages),
                    system=request.system,
                )
            else:
                sdk_response = self._sdk.messages.create(
                    model=request.model,
                    max_tokens=request.max_tokens,
                    messages=_build_sdk_messages(request.messages),
                )
        except anthropic.APIStatusError as exc:
            raise APIError(str(exc), status_code=exc.status_code) from exc
        except anthropic.APIConnectionError as exc:
            raise APIError(f"Connection failed: {exc}") from exc

        return self._map_response(sdk_response)

    def stream_chat(self, request: ChatRequest) -> Iterator[str]:
        """Stream a chat request, yielding text deltas one chunk at a time.

        Args:
            request: The fully-specified chat request.

        Yields:
            Text delta strings as they are generated.

        Raises:
            APIError: When the upstream API returns an error.
        """
        try:
            if request.system is not None:
                stream_ctx = self._sdk.messages.stream(
                    model=request.model,
                    max_tokens=request.max_tokens,
                    messages=_build_sdk_messages(request.messages),
                    system=request.system,
                )
            else:
                stream_ctx = self._sdk.messages.stream(
                    model=request.model,
                    max_tokens=request.max_tokens,
                    messages=_build_sdk_messages(request.messages),
                )
            with stream_ctx as stream:
                yield from stream.text_stream
        except anthropic.APIStatusError as exc:
            raise APIError(str(exc), status_code=exc.status_code) from exc
        except anthropic.APIConnectionError as exc:
            raise APIError(f"Connection failed: {exc}") from exc

    @staticmethod
    def _map_response(sdk_response: anthropic.types.Message) -> ChatResponse:
        """Map an Anthropic SDK ``Message`` to our ``ChatResponse`` model."""
        content_blocks: list[ContentBlock] = []
        for block in sdk_response.content:
            text = block.text if block.type == "text" else ""
            content_blocks.append(ContentBlock(type=block.type, text=text))

        usage = sdk_response.usage
        return ChatResponse(
            id=sdk_response.id,
            model=sdk_response.model,
            content=content_blocks,
            stop_reason=sdk_response.stop_reason,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
        )
