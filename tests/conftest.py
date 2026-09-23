# /src/tests/conftest.py

from collections.abc import Iterator

import pytest

from apiframework.services.booking_service import BookingService


@pytest.fixture
def booking_service() -> Iterator[BookingService]:
    with BookingService() as service:
        yield service
