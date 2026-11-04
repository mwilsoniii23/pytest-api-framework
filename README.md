# Restful-Booker API Test Automation Framework [![Status: In Progress](https://img.shields.io/badge/Status-In%20Progress-yellow.svg)](https://github.com/mwilsoniii23/pytest-api-framework)

> **Status:** 🚧 **In Progress** — Active development, test coverage expansion, and CI hardening ongoing.

A production-grade, enterprise-ready API test automation framework built with **Python**, **PyTest**, and **PyTest-BDD**. Tailored against the Restful-Booker platform, this framework combines full BDD feature scenarios, Pydantic domain models, service-level API abstraction, contract verification against OpenAPI specs, and targeted unit test coverage.

---

## Key Features

* **Hybrid Testing Strategy**: Complete coverage through BDD feature files (`.feature`), functional integration suites, and isolated internal unit tests.
* **Service Object Pattern**: Clean separation between raw HTTP clients (`src/apiframework/http/`), service domain logic (`booking_service.py`), and test scripts.
* **Pydantic Schema Models**: Strongly-typed data models (`booking.py`) for automated request serialization and response validation.
* **OpenAPI Contract & Conformance Testing**: Contract checks and conformance tests against `docs/openapi.yaml` to guarantee spec compliance and catch API drifts early.
* **TestData Builders & Factories**: Dynamic test data generation using custom builder patterns (`support/builders.py`, `factories.py`).
* **Defect & Bug Tracking**: Dedicated defect coverage tests (`test_defect_coverage.py`) mapped to explicit bug documentation in `docs/bugs-found.md`.

---

## Project Structure

```text
pytest-api-framework/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI workflow pipeline (uv-powered)
├── docs/
│   ├── bugs-found.md              # Documented API defects and reproduction steps
│   └── openapi.yaml               # OpenAPI specification contract
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
├── pyproject.toml / requirements.txt
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
   uv pip install -e .
   ```

---

## Running Tests

### Run Full Test Suite
Executes all functional, BDD, and unit tests:
```bash
pytest
```
*(Tip: You can also run tests instantly without manual activation using `uv run pytest`)*

### Run Unit Tests Only
Verify internal framework components (services, builders, client logic):
```bash
pytest tests/unit/
```

### Run Functional & BDD Scenarios
Execute end-to-end API lifecycle and feature scenarios:
```bash
pytest tests/functional/
```

### Run OpenAPI Contract Conformance Tests
Validate that API responses strictly adhere to the OpenAPI spec:
```bash
pytest tests/functional/test_openapi_conformance.py tests/unit/test_openapi_contract.py
```

### Run Defect Verification Tests
Run regression checks specifically covering known API defects:
```bash
pytest tests/unit/test_defect_coverage.py
```

---

## Continuous Integration (CI/CD)

This repository includes an automated CI pipeline configured with **GitHub Actions** (`.github/workflows/ci.yml`). It leverages **`uv`** for lightning-fast dependency caching and installation on every push and pull request to `main`.

### Example Workflow Configuration (`.github/workflows/ci.yml`)

```yaml
name: API Test Automation Pipeline

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          uv pip install --system -e .

      - name: Run PyTest Suite
        run: |
          pytest --verbose --tb=short
```

---

## Architecture Overview

1. **HTTP Client Factory (`http/factory.py`)**: Manages session creation, base URLs, and authentication header injection.
2. **Service Layer (`services/booking_service.py`)**: Wraps endpoints into strongly-typed methods returning domain models or HTTP response wrappers.
3. **Pydantic Validation (`models/booking.py`)**: Ensures strict type-checking on request payloads and response contracts.
4. **Data Builders (`support/builders.py`)**: Provides fluent interfaces to generate valid or edge-case payload data dynamically for testing.

---

## Documentation & Bug Tracking

* **OpenAPI Spec**: See `docs/openapi.yaml` for the complete API spec definition used in contract testing.
* **Bug Log**: Detailed defect tracking and edge-case behaviors uncovered during test automation are documented in `docs/bugs-found.md`.