# tests/functional/test_create_booking.py

import contextlib

import pytest

from apiframework.http.client import ApiClient
from apiframework.services.booking_service import BookingApiError, BookingService


@pytest.mark.integration
def test_create_booking_requires_additionalneeds() -> None:
    payload = {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-10-30", "checkout": "2023-10-31"},
    }

    with ApiClient() as client, BookingService() as service:
        response = client.post("/booking", json=payload)

        try:
            assert response.status_code == 400
        finally:
            if response.is_success:
                created_booking_id = response.json()["bookingid"]
                with contextlib.suppress(BookingApiError):
                    service.delete_booking(created_booking_id)
