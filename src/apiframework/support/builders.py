# src/apiframework/support/builders.py

from datetime import date
from typing import Self

from apiframework.models.booking import Booking, BookingDates
from apiframework.support.factories import BookingFactory, unique_booking_name


class BookingBuilder:
    """Readable test-data builder for intentional booking payloads."""

    def __init__(self) -> None:
        self._booking = BookingFactory.build()

    def with_firstname(self, firstname: str) -> Self:
        self._booking.firstname = firstname
        return self

    def with_lastname(self, lastname: str) -> Self:
        self._booking.lastname = lastname
        return self

    def with_unique_name(self, prefix: str = "Auto") -> Self:
        self._booking.firstname = unique_booking_name(f"{prefix}-First")
        self._booking.lastname = unique_booking_name(f"{prefix}-Last")
        return self

    def with_totalprice(self, totalprice: int) -> Self:
        self._booking.totalprice = totalprice
        return self

    def with_dates(self, checkin: date, checkout: date) -> Self:
        self._booking.booking_dates = BookingDates(checkin=checkin, checkout=checkout)
        return self

    def without_deposit(self) -> Self:
        self._booking.depositpaid = False
        return self

    def without_additional_needs(self) -> Self:
        self._booking.additionalneeds = None
        return self

    def build(self) -> Booking:
        return self._booking.model_copy(deep=True)
