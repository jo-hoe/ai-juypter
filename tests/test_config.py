"""Tests for ProxyConfig validation and construction.

No monkeypatching of os.environ.  ProxyConfig is constructed directly with
explicit values so the tests are hermetic.
"""
import os

import pytest
from pydantic import ValidationError

from ai_client.config import ProxyConfig
from ai_client.exceptions import ConfigurationError


class TestProxyConfigConstruction:
    def test_valid_minimal(self) -> None:
        config = ProxyConfig(auth_token="sk-test")
        assert config.auth_token == "sk-test"
        assert "api.anthropic.com" in str(config.base_url)

    def test_valid_with_custom_base_url(self) -> None:
        config = ProxyConfig(
            auth_token="sk-test",
            base_url="http://localhost:6655/anthropic/",  # type: ignore[arg-type]
        )
        assert "localhost" in str(config.base_url)

    def test_blank_auth_token_raises(self) -> None:
        with pytest.raises((ConfigurationError, ValidationError)):
            ProxyConfig(auth_token="   ")

    def test_empty_auth_token_raises(self) -> None:
        with pytest.raises((ValidationError, ConfigurationError)):
            ProxyConfig(auth_token="")

    def test_invalid_base_url_raises(self) -> None:
        with pytest.raises((ValidationError, ConfigurationError)):
            ProxyConfig(
                auth_token="sk-test",
                base_url="not-a-url",  # type: ignore[arg-type]
            )

    def test_frozen_config_is_immutable(self) -> None:
        config = ProxyConfig(auth_token="sk-test")
        with pytest.raises((TypeError, ValidationError)):
            config.auth_token = "new-value"  # type: ignore[misc]

    def test_base_url_str_strips_trailing_slash(self) -> None:
        config = ProxyConfig(
            auth_token="sk-test",
            base_url="http://localhost:6655/anthropic/",  # type: ignore[arg-type]
        )
        assert not config.base_url_str.endswith("/")

    def test_openai_fields_optional(self) -> None:
        config = ProxyConfig(auth_token="sk-test")
        assert config.openai_api_key is None
        assert config.openai_base_url is None

    def test_openai_fields_accepted(self) -> None:
        config = ProxyConfig(
            auth_token="sk-test",
            openai_api_key="oai-key",
            openai_base_url="http://localhost:6655/openai/v1",  # type: ignore[arg-type]
        )
        assert config.openai_api_key == "oai-key"


class TestProxyConfigFromEnv:
    def test_from_env_raises_without_auth_token(self) -> None:
        """from_env() must raise ConfigurationError when the var is absent.

        Skipped when ANTHROPIC_AUTH_TOKEN happens to be set in the test runner.
        """
        if os.environ.get("ANTHROPIC_AUTH_TOKEN"):
            pytest.skip("ANTHROPIC_AUTH_TOKEN is set in the environment; skipping.")
        with pytest.raises(ConfigurationError, match="ANTHROPIC_AUTH_TOKEN"):
            ProxyConfig.from_env()
