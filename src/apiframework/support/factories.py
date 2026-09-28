# src/apiframework/support/factories.py

from datetime import date, timedelta
from uuid import uuid4

from polyfactory.factories.pydantic_factory import ModelFactory

from apiframework.models.booking import Booking, BookingDates


def unique_booking_name(prefix: str = "Auto") -> str:
    """Return a unique, API-safe name for tests running against a shared instance."""
    return f"{prefix}-{uuid4().hex}"


class BookingDatesFactory(ModelFactory[BookingDates]):
    __model__ = BookingDates

    @classmethod
    def checkin(cls) -> date:
        return date.today() + timedelta(days=30)

    @classmethod
    def checkout(cls) -> date:
        return date.today() + timedelta(days=31)


class BookingFactory(ModelFactory[Booking]):
    __model__ = Booking

    @classmethod
    def firstname(cls) -> str:
        return unique_booking_name("First")

    @classmethod
    def lastname(cls) -> str:
        return unique_booking_name("Last")

    @classmethod
    def totalprice(cls) -> int:
        return 111

    @classmethod
    def depositpaid(cls) -> bool:
        return True

    @classmethod
    def booking_dates(cls) -> BookingDates:
        return BookingDatesFactory.build()

    @classmethod
    def additionalneeds(cls) -> str:
        return "Breakfast"
