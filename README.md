# AI Jupyter Devcontainer Template

[![CI](https://github.com/jo-hoe/ai-juypter/actions/workflows/ci.yml/badge.svg)](https://github.com/jo-hoe/ai-juypter/actions/workflows/ci.yml)

A JupyterLab devcontainer that wires together:

- **JupyterLab** (via `quay.io/jupyter/scipy-notebook`)
- **Claude Code** (via devcontainer feature)
- **Jupyter AI** (pre-configured for `anthropic/claude-sonnet-latest`)
- **`ai_client`** — a locally-installable, strongly-typed Python package that wraps the Anthropic SDK

API credentials are injected at runtime from your local environment — no proxy-specific code or brand references appear anywhere in this repo.

---

## Quick start

### 1. Prerequisites

- [VS Code](https://code.visualstudio.com/) with the
  [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Docker Desktop (or a Docker-compatible runtime)

### 2. Set environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# edit .env with your values
```

The variables read by the devcontainer:

| Variable               | Purpose                                  |
|------------------------|------------------------------------------|
| `ANTHROPIC_AUTH_TOKEN` | Auth token for the Anthropic API         |
| `ANTHROPIC_BASE_URL`   | Custom base URL (proxy override)         |
| `OPENAI_API_KEY`       | Auth key for the OpenAI-compatible API   |
| `OPENAI_BASE_URL`      | Custom base URL for OpenAI endpoint      |

### 3. Open in devcontainer

```
F1 → Dev Containers: Reopen in Container
```

VS Code builds the image, runs `pip install -r requirements.txt`, and launches JupyterLab on port 8888.

### 4. Run tests

Inside the container terminal:

```bash
pytest --cov=ai_client --cov-report=term-missing
```

### 5. Try the example notebook

Open `notebooks/01_ai_data_analysis.ipynb` in JupyterLab and run all cells.

---

## Project layout

```
.
├── .devcontainer/
│   ├── devcontainer.json   # devcontainer spec
│   └── Dockerfile          # optional image extension
├── .jupyter/
│   └── jupyter_ai_config.py  # Jupyter AI defaults
├── src/
│   └── ai_client/          # installable typed package
│       ├── __init__.py
│       ├── client.py
│       ├── config.py
│       ├── exceptions.py
│       ├── models.py
│       └── py.typed
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_config.py
│   └── test_models.py
├── notebooks/
│   └── 01_ai_data_analysis.ipynb
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

---

## `ai_client` package

### `ProxyConfig`

Reads four standard environment variables:

```python
from ai_client import ProxyConfig

config = ProxyConfig.from_env()
# or construct directly:
config = ProxyConfig(
    auth_token="sk-...",
    base_url="http://localhost:6655/anthropic/",
)
```

### `AIClient`

```python
from ai_client import AIClient, ChatMessage, ChatRequest, ProxyConfig

config = ProxyConfig.from_env()
client = AIClient(config)

request = ChatRequest(
    model="claude-sonnet-latest",
    messages=[ChatMessage(role="user", content="Hello!")],
)

# Blocking
response = client.chat(request)
print(response.content[0].text)

# Streaming
for chunk in client.stream_chat(request):
    print(chunk, end="", flush=True)
```
