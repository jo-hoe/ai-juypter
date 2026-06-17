# Jupyter AI configuration loaded at server startup via the Jupyter traitlets
# config system.  The name ``AiExtension`` matches the jupyter_ai extension.
#
# No proxy-specific names appear here — only standard Anthropic env-var names.

c = get_config()  # type: ignore[name-defined]  # noqa: F821 — injected by Jupyter

# Default model: provider-id:model-id format required by jupyter-ai>=2.0
c.AiExtension.default_language_model = "anthropic:claude-sonnet-latest"

# Map the Anthropic provider to the standard env var that holds the API key.
c.AiExtension.api_keys = {
    "anthropic": "ANTHROPIC_AUTH_TOKEN",
}
