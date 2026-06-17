.PHONY: all install test lint format type-check check pre-commit clean

all: install check

install:
	pip install -e .[dev]
	pre-commit install

test:
	pytest -v --cov=ai_client --cov-report=term-missing --cov-fail-under=90

lint:
	ruff check src tests

format:
	ruff format src tests

type-check:
	mypy src/ai_client tests

check: lint type-check test

pre-commit:
	pre-commit run --all-files

clean:
	pip uninstall -y ai-client
	pre-commit uninstall
