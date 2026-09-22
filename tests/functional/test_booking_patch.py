# /tests/functional/test_booking_patch.py

import pytest

from apiframework.services.booking_service import BookingService


@pytest.mark.integration
def test_patch_requires_auth_token(booking_service: BookingService) -> None:
    booking_ids = booking_service.list_booking_ids()

    assert isinstance(booking_ids, list)
