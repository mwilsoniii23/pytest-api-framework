# /tests/functional/test_booking_patch.py
import contextlib

import pytest

from apiframework.http.client import ApiClient
from apiframework.services.booking_service import BookingApiError, BookingService
from apiframework.support import BookingBuilder


@pytest.mark.integration
def test_patch_without_auth_token_is_rejected() -> None:
    """Booker requires a token for PATCH despite /auth documenting only PUT and DELETE

    See docs/bugs-found.md #16
    """
    with BookingService() as service, ApiClient() as client:
        booking = BookingBuilder().with_unique_name("NoAuth").build()
        created = service.create_booking(booking)
        try:
            response = client.request(
                "PATCH",
                f"/booking/{created.bookingid}",
                json={"firstname": "NoAuth"},
            )
            assert response.status_code == 403
        finally:
            with contextlib.suppress(BookingApiError):
                service.delete_booking(created.bookingid)
