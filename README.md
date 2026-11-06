# Restful-Booker API Test Automation Framework [![CI](https://github.com/mwilsoniii23/pytest-api-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/mwilsoniii23/pytest-api-framework/actions/workflows/ci.yml)

> **Status:** 🚧 **In Progress** — Core framework complete.  BDD feature scenarios, Docker packaging, and Allure reporting in progress.

An API test automation framework with strict typing, contract validation, and property-based fuzzing.
The framework tests [Restful-Booker](https://restful-booker.herokuapp.com/apidoc/index.html) API endpoints using a hybrid approach, combining:
   - BDD feature scenarios
   - Pydantic-validated domain models
   - HTTPX client with granular timeouts and transport-level retries
   - Property-based contract testing with Schemathesis
   - and rigorous type-checking

Restful-Booker does not publish a machine-readable contract, so this project includes a `docs/openapi.yaml` file, authored from the apiDoc (https://restful-booker.herokuapp.com/apidoc/api_data.json).
Testing against it found **nine defects**, documented in docs/bugs-found.md with a regression test for each.


Defects were identified in four ways:
1. Close reading of the published documentation and manual testing
2. Targeted negative testcases
3. Automated contract validation against `docs/openapi.yaml`
4. Automated property-based contract testing with Schemathesis

The fuzzer found the two most serious - `POST /auth` returns `200 OK` on failed authentication, and malformed query parameters crash the server.

**Stack:** pytest · httpx · pydantic · pytest-bdd · Schemathesis · uv

---

## Key Features

* **Hybrid Testing Strategy**: Complete coverage through BDD feature files (`.feature`), functional integration suites, and isolated internal unit tests.
* **Service Object Pattern**: Clean separation between raw HTTP clients (`src/apiframework/http/`), service domain logic (`booking_service.py`), and test scripts.
* **Pydantic Schema Models**: Strongly typed data models (`booking.py`) for automated request serialization and response validation.
* **OpenAPI Contract & Conformance Testing**: Contract checks and conformance tests against `docs/openapi.yaml` to guarantee spec compliance and catch API drifts early.
* **TestData Builders & Factories**: Dynamic test data generation using custom builder patterns (`support/builders.py`, `factories.py`).
* **Defect & Bug Tracking**: Dedicated tests (`test_defect_coverage.py`) ensuring mapped to explicit bug documentation in `docs/bugs-found.md`.

---

## Project Structure

```text
pytest-api-framework/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI workflow pipeline (uv-powered)
├── docs/
│   ├── bugs-found.md              # Documented API defects and reproduction steps
│   └── openapi.yaml               # OpenAPI specification for Restful-Booker API, authored from their docs since the API does not provide an OpenAPI spec
├── src/
│   └── apiframework/
│       ├── config/                # Environment and app setting management
│       ├── http/                  # Base HTTP client wrappers, Auth, & Client factories
│       ├── models/                # Pydantic domain models (Booking, Auth payloads)
│       ├── services/              # API Service layer (BookingService wrappers)
│       └── support/               # Test data builders & factories
├── tests/
│   ├── conftest.py                # Global PyTest fixtures (clients, auth, config)
│   ├── functional/                # BDD & end-to-end functional test suites
│   │   ├── bdd_features.py        # PyTest-BDD runner mapping
│   │   ├── features/              # Gherkin scenarios (.feature files)
│   │   └── steps/                 # Step definitions for BDD scenarios
│   └── unit/                      # Isolated unit tests for framework components
├── pyproject.toml
└── README.md
```

---

## Quick Start

### Prerequisites

* **Python 3.12+**
* **`uv`**: Fast Python package installer and resolver ([Installation Guide](https://github.com/astral-sh/uv))

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/mwilsoniii23/pytest-api-framework.git
   cd pytest-api-framework
   ```

2. **Create Virtual Environment and Install Dependencies with `uv`**
   ```bash
   # Create virtual environment
   uv venv

   # Activate environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install package and dependencies in editable mode
   uv sync
   ```

---

## Running Tests

### Run Full Test Suite
Executes all functional, BDD, and unit tests:
```bash
uv run pytest
```

### Run Unit Tests Only
Verify internal framework components (services, builders, client logic):
```bash
uv run pytest tests/unit/
```

### Run Functional & BDD Scenarios
Execute end-to-end API lifecycle and feature scenarios:
```bash
uv run pytest tests/functional/
```

### Run OpenAPI Contract Conformance Tests
Validate that API responses strictly adhere to the OpenAPI spec:
```bash
pytest tests/functional/test_openapi_conformance.py tests/unit/test_openapi_contract.py
```

### Run Defect Verification Tests
Validate bugs in bugs-found.md mapped to explicit test cases:
```bash
pytest tests/unit/test_defect_coverage.py
```

---

## Continuous Integration (CI/CD)

This repository includes an automated CI pipeline configured with **GitHub Actions** (`.github/workflows/ci.yml`). It leverages **`uv`** for lightning-fast dependency caching and installation on every push and pull request to `main`.

### Example Workflow Configuration (`.github/workflows/ci.yml`)

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --locked

      - name: Lint
        run: uv run ruff check .

      - name: Format check
        run: uv run ruff format --check .

      - name: Type check
        run: uv run mypy src

      - name: Test
        run: uv run pytest -v
```

---

## Architecture Overview

1. **HTTP Client Factory (`http/factory.py`)**: Manages session creation, base URLs, and builds an httpx.Client instance with timeouts.
2. **Auth Factory (`http/auth.py`)**: Manages authentication header injection and token refresh.
3. **Service Layer (`services/booking_service.py`)**: Wraps endpoints into strongly typed methods returning domain models or HTTP response wrappers.
4. **Pydantic Validation (`models/booking.py`)**: Ensures strict type-checking on request payloads and response contracts.
5. **Data Builders (`support/builders.py`)**: Provides fluent interfaces to generate valid or edge-case payload data dynamically for testing.

---

## Documentation & Bug Tracking

* **OpenAPI Spec**: See `docs/openapi.yaml` for the complete API spec definition used in contract testing.
* **Bug Log**: Detailed defect tracking and edge-case behaviors uncovered during test automation are documented in `docs/bugs-found.md`.