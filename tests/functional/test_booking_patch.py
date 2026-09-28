# /tests/functional/test_booking_patch.py
import contextlib

import pytest

from apiframework.models.booking import PartialBooking
from apiframework.services.booking_service import BookingApiError, BookingService
from apiframework.support.builders import BookingBuilder


@pytest.mark.integration
def test_can_find_created_booking_by_unique_generated_name(
    booking_service: BookingService,
) -> None:
    booking = BookingBuilder().with_unique_name("Functional").build()
    created_booking_id: int | None = None

    try:
        created = booking_service.create_booking(booking)
        created_booking_id = created.bookingid

        booking_ids = booking_service.list_booking_ids(
            firstname=booking.firstname,
            lastname=booking.lastname,
        )

        assert created.booking == booking
        assert created_booking_id in {item.bookingid for item in booking_ids}
    finally:
        if created_booking_id is not None:
            with contextlib.suppress(BookingApiError):
                booking_service.delete_booking(created_booking_id)


@pytest.mark.integration
def test_patch_updates_booking_created_by_this_test(
    booking_service: BookingService,
) -> None:
    booking = BookingBuilder().with_unique_name("Patch").build()
    created_booking_id: int | None = None

    try:
        created = booking_service.create_booking(booking)
        created_booking_id = created.bookingid

        patched = booking_service.partial_update_booking(
            created_booking_id,
            PartialBooking(firstname="Patched"),
        )

        assert patched.firstname == "Patched"
    finally:
        if created_booking_id is not None:
            with contextlib.suppress(BookingApiError):
                booking_service.delete_booking(created_booking_id)
