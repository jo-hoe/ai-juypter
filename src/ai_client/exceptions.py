"""Custom exceptions for the ai_client package."""


class AIClientError(Exception):
    """Base exception for all ai_client errors."""


class ConfigurationError(AIClientError):
    """Raised when the client configuration is invalid or incomplete."""


class APIError(AIClientError):
    """Raised when the upstream API returns an error response."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
