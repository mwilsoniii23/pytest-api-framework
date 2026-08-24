# pytest-api-framework

Production-grade Python API test framework - pytest, httpx, pydantic contract validation.

**Status:** IN ACTIVE DEVELOPMENT

[x] Config
[x] HTTP Client
[x] Auth
[x] Models
[ ] unit tests
[ ] integration tests
[ ] contract validation
[x] logging
[ ] service layer
[ ] BDD
[ ] Docker
[ ] CI/CD
[ ] Reporting

## Quickstart

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/mwilsoniii23/pytest-api-framework
cd pytest-api-framework
uv sync
uv run pytest
```

## What's covered
## Project layout
## Running tests

## Running tests

```bash
uv run pytest                     # unit tests only - no network
uv run pytest -m integration      # hits the live Restful Booker API
uv run mypy src                   # strict type checking
uv run ruff check .               # lint
```

## Configuration

All settings are environment variables prefixed `BOOKER_`.

| Variable          | Default                                | Purpose           |
|-------------------|----------------------------------------|-------------------|
| `BOOKER_BASE_URL` | `https://restful-booker.herokuapp.com` | System Under Test |

## Design decisions
#TODO: write up something on the Schema Drift issue

## Defects found
| #                                                                     | Severity | Type      | Endpoint              | Summary                                                                               | Test                                                                     |
|-----------------------------------------------------------------------|----------|-----------|-----------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| [#17](https://github.com/mwilsoniii23/pytest-api-framework/issues/17) | 3-Medium | Framework | `PATCH /booking/{id}` | PATCH Requires an auth token, but the `/auth` documentation lists only PUT and DELETE | `tests/functional/test_booking_patch.py::test_patch_requires_auth_token` |

---

## #17 — client.patch() sends unauthenticated requests.

**Severity:** 3-Medium
**Type:** Framework defect — PATCH tests will not work because the API requires authentication.
**Endpoint:** `PATCH /booking/{id}`

**Repro**
```bash
curl -i -X PATCH https://restful-booker.herokuapp.com/booking/910 \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "firstname":"James",
    "lastname":"Brown"
    }'
```