# tests/unit/test_openapi_contract.py

from pathlib import Path

import yaml

from apiframework.models.booking import Booking


def test_openapi_booking_schema_matches_model() -> None:
    """The spec and the model must describe the same shape."""
    spec = yaml.safe_load(Path("docs/openapi.yaml").read_text())
    spec_schema = spec["components"]["schemas"]["Booking"]
    model_schema = Booking.model_json_schema(by_alias=True)

    assert set(spec_schema["required"]) == set(model_schema["required"])
    assert set(spec_schema["properties"]) == set(model_schema["properties"])
