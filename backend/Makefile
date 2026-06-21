.PHONY: lint format type test check run

lint:
	uv run ruff check .

format:
	uv run ruff check --fix .
	uv run black .

type:
	uv run mypy app

test:
	uv run pytest

check: lint type test

# works after phase 4
run:
	uv run uvicorn app.main:app --reload