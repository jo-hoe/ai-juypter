"""ai_client — strongly-typed Anthropic client wrapper.

Public surface::

    from ai_client import AIClient, ChatMessage, ChatRequest, ChatResponse, ProxyConfig
"""
from .client import AIClient
from .config import ProxyConfig
from .exceptions import AIClientError, APIError, ConfigurationError
from .models import ChatMessage, ChatRequest, ChatResponse, ContentBlock

__all__ = [
    "AIClient",
    "AIClientError",
    "APIError",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ConfigurationError",
    "ContentBlock",
    "ProxyConfig",
]
