Production-grade Python API test framework - pytest, httpx, pydantic contract validation.
IN ACTIVE DEVELOPMENT

to verify a commit is clean:
uv run pytest -v
uv run mypy src
uv run ruff check .

if all are GREEN, proceed with commit.