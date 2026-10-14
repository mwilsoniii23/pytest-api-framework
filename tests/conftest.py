# /src/tests/conftest.py

from collections.abc import Iterator
from pathlib import Path

import pytest

from apiframework.services.booking_service import BookingService

SPEC_PATH = Path(__file__).resolve().parents[1] / "docs" / "openapi.yaml"


@pytest.fixture
def booking_service() -> Iterator[BookingService]:
    with BookingService() as service:
        yield service
