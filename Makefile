.PHONY: all install test lint format type-check check clean

all: install check

install:
	pip install -e .[dev]

test:
	pytest -v --cov=ai_client --cov-report=term-missing --cov-fail-under=90

lint:
	ruff check src tests

format:
	ruff format src tests

type-check:
	mypy src/ai_client tests

check: lint type-check test

clean:
	pip uninstall -y ai-client
