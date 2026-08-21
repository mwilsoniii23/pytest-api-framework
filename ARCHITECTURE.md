# Architecture & Design Decisions

# Architecture

**Status:** in active development.  Config and scaffolding are in place.

**TODO:**
- [ ] HTTP client
- [ ] service layer
- [ ] test suites
- [ ] reporting

Decisions below reflect what exists today.

---
## 1. Project layout
```aiignore
src/apiframework/
  config/
  http/
  models/
tests/
  unit/
```

### `src/` layout

Test code imports the *installed* package, not the files in the working directory. Without the `src/` layout, 
test code would need to import from the working directory, which would be fragile and error-prone.

Therefore, the package must be installed in the working directory for tests to work.  This is deliberate.  Failures 
should surface on commits rather than at distribution time.

### Package configuration

The project is an installable package, and uses [pyproject.toml](https://www.python.org/dev/peps/pep-0518/) for configuration.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/apiframework"]
```

'uv sync' installs it in editable mode. Source edits take effect immediately; imports still resolve through the 
installed package.

**Rejected alternative:**
- [ ] setting `pythonpath = ["src"]` in the pytest config.
    It fixes imports for pytest, but nothing else.
    It substitutes a test-runner setting for package configuration and hides the problem rather than fixing it.

---

# 2. Toolchain

| Choice          | Over                             | Reasoning                                                                               |
|-----------------|----------------------------------|-----------------------------------------------------------------------------------------|
| `uv`            | pip / poetry / pipenv            | `uv` is a lightweight alternative to `pipenv`.                                          | 
|                 |                                  | It is more flexible and substantially faster than `pipenv` and has a smaller footprint. |
|                 |                                  | `uv.lock` is committed so environments are reproducible.                                |
| `ruff`          | flake8 + black + isort + plugins | `ruff` is a fast linter for Python.                                                     |
|                 |                                  | Replaces an entire ecosystem with no loss of coverage.                                  |
| `mypy --strict` | untyped or lenient typing        | Strict mode enforces type checking                                                      |
|                 |                                  | Reducing preventable bugs                                                               |
|                 |                                  | See §4.                                                                                 |
| `pytest`        | unittest                         | Fixtures, parametrization, and more.                                                    |
| `pre-commit`    | manual discipline                | Hooks in version control, so gates stick with the repo, not local `.git/hooks`.         |
| `pydantic` v2   | jsonschema / manual validation   | Models serve as typed test data                                                         |
| `httpx`         | requests                         | HTTP client. Sync and async through one API.                                            |

### Python 3.12

Started the project on Python 3.14, but encountered compatibility issues with `pytest-asyncio`. Pinned to 3.12, 
since that version will be the most widely compatible.

### Lint rule selection

```toml
[tool.ruff.lint]
select = [
    "E",
    "F",
    "I",
    "N",
    "UP",
    "B",
    "SIM"
    ]
```
`B` (bugbear) catches defect-patterns -- mutable default arguments, loop variable binding in closures.
and `UP` (pyupgrade) rewrites outdated syntax automagically.

---

## 3. Quality Gates

### Pre-commit

`ruff` (with `--fix`), `ruff-format`, `mypy`, and 'gitleaks` run on every commit.

### Gitleaks

`gitleaks` runs on every commit, scanning for secrets and other sensitive information.

### Test runner configuration

```toml
adopts = "-ra --strict-markers"
```

`--strict-markers` turns an undeclared marker into an error.
A typo'd marker otherwise silently fails and reports a SUCCESS – a false green run

`-ra` reports skips and xfails in the summary, so tests that aren't running are visible rather than buried.

**This is the recurring principle in this project:** the dangerous state is not a failing check, it is a passing
check that isn't checking anything.

---

## 4. Type checking

`mypy` runs in `strict` mode on every commit, checking for type errors.

```toml
[tool.mypy]
plugins = ["pydantic.mypy"]
strict = true
warn_unreachable = true
```

models *are* the contract assertions
- they are the test data
- they are the documentation
- they are the source of truth

In designing the pydantic models for booking payloads, I considered the following:
- the payloads are the contract assertions
- the payloads are the documentation
- the payloads are the source of truth

Therefore, unknown fields in a response are flagged as errors.  This allows for schema drift detection.
The tradeoff is that the test runs may be more brittle as unknown changes to the payloads will cause test failures.
That's as it should be, though.