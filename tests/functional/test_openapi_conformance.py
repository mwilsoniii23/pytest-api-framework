# tests/functional/test_openapi_conformance.py
from typing import Any

import pytest
import schemathesis
from hypothesis import settings

from apiframework.config.settings import get_settings

schema = schemathesis.openapi.from_path("docs/openapi.yaml")

DESTRUCTIVE = {"PUT", "PATCH", "DELETE"}


@pytest.mark.fuzz
@schema.parametrize()
@settings(max_examples=20, deadline=None)
def test_api_conforms_to_spec(case: schemathesis.Case[Any]) -> None:
    """Fuzz the documented API contract. Skips mutating operations -
    Booker is a shared public instance, and generated IDs would hit other people's data."""
    if case.method.upper() in DESTRUCTIVE:
        pytest.skip("mutating operation not fuzzed against a shared instance")

    case.call_and_validate(base_url=str(get_settings().base_url))
