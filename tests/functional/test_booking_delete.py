# tests/functional/test_booking_delete.py

import contextlib

import pytest

from apiframework.http.client import ApiClient
from apiframework.services.booking_service import BookingApiError, BookingService
from apiframework.support.builders import BookingBuilder


@pytest.mark.integration
@pytest.mark.xfail(
    reason="Booker returns 201 Created on delete; see docs/bugs-found.md #40",
    strict=True,
)
def test_delete_booking_returns_success_status() -> None:
    """DELETE should return 200, 202, or 204 for a successful delete"""
    with BookingService() as service, ApiClient() as client:
        booking = BookingBuilder().with_unique_name("Delete").build()
        created = service.create_booking(booking)

        response = client.delete(
            f"/booking/{created.bookingid}",
            headers={"Accept": "application/json"},
        )

        try:
            assert response.status_code in (200, 202, 204)
        finally:
            if response.status_code not in {200, 202, 204}:
                with contextlib.suppress(BookingApiError):
                    service.delete_booking(created.bookingid)
