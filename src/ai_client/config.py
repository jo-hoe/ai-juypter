"""Runtime configuration loaded from environment variables.

``ProxyConfig`` is intentionally immutable after construction — all fields are
declared with ``frozen=True`` via Pydantic so that accidental mutation is a
type error at both static analysis time and at runtime.
"""

from __future__ import annotations

import os
from typing import Annotated

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator

from .exceptions import ConfigurationError

_DEFAULT_BASE_URL = AnyHttpUrl("https://api.anthropic.com")


class ProxyConfig(BaseModel):
    """Strongly-typed, immutable configuration for the AI proxy.

    Reads ``ANTHROPIC_AUTH_TOKEN`` and ``ANTHROPIC_BASE_URL`` from the
    environment.  ``OPENAI_API_KEY`` / ``OPENAI_BASE_URL`` are preserved so
    that callers can also interrogate them if needed; the ``AIClient`` itself
    only uses the Anthropic variables.
    """

    model_config = ConfigDict(frozen=True)

    auth_token: Annotated[str, Field(min_length=1)] = Field(
        ...,
        description="Anthropic auth token (ANTHROPIC_AUTH_TOKEN).",
    )
    base_url: AnyHttpUrl = Field(
        default=_DEFAULT_BASE_URL,
        description="Anthropic base URL (ANTHROPIC_BASE_URL).",
    )
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key (OPENAI_API_KEY).",
    )
    openai_base_url: AnyHttpUrl | None = Field(
        default=None,
        description="OpenAI base URL (OPENAI_BASE_URL).",
    )

    @model_validator(mode="after")
    def _validate_auth(self) -> ProxyConfig:
        if not self.auth_token.strip():
            raise ConfigurationError(
                "auth_token must not be blank. "
                "Set the ANTHROPIC_AUTH_TOKEN environment variable."
            )
        return self

    @classmethod
    def from_env(cls) -> ProxyConfig:
        """Construct a ``ProxyConfig`` from standard environment variables.

        Raises:
            ConfigurationError: When required variables are absent.
        """
        auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
        if not auth_token:
            raise ConfigurationError(
                "Required environment variable ANTHROPIC_AUTH_TOKEN is not set."
            )

        raw_base_url = os.environ.get("ANTHROPIC_BASE_URL")
        raw_openai_key = os.environ.get("OPENAI_API_KEY")
        raw_openai_base = os.environ.get("OPENAI_BASE_URL")

        return cls(
            auth_token=auth_token,
            base_url=AnyHttpUrl(raw_base_url) if raw_base_url else _DEFAULT_BASE_URL,
            openai_api_key=raw_openai_key or None,
            openai_base_url=AnyHttpUrl(raw_openai_base) if raw_openai_base else None,
        )

    @property
    def base_url_str(self) -> str:
        """Return the base URL as a plain string, stripped of any trailing slash."""
        return str(self.base_url).rstrip("/")
