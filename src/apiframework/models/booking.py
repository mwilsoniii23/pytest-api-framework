# /src/apiframework/models/booking.py

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    """Base model for API payloads.

    Allows Pythonic field names in code while still supporting API aliases
    during validation and serialization.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )


class BookingDates(ApiModel):
    """Nested booking date range model.

    Pydantic parses ISO date strings like "2018-01-01" into datetime.date objects.
    """

    checkin: date
    checkout: date


class Booking(ApiModel):
    """Booking request/response payload.

    API field:
        bookingdates

    Python field:
        booking_dates
    """

    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    booking_dates: BookingDates = Field(alias="bookingdates")
    additionalneeds: str | None = None


class PartialBooking(ApiModel):
    """Partial booking payload for PATCH /booking/{id}.

    Every field is optional because PATCH can update any subset of booking fields.
    """

    firstname: str | None = None
    lastname: str | None = None
    totalprice: int | None = None
    depositpaid: bool | None = None
    booking_dates: BookingDates | None = Field(default=None, alias="bookingdates")
    additionalneeds: str | None = None


class CreateBookingResponse(ApiModel):
    """Response envelope returned by POST /booking.

    Shape:
        {
            "bookingid": int,
            "booking": Booking
        }
    """

    bookingid: int
    booking: Booking


class AuthRequest(ApiModel):
    """Auth request payload for POST /auth."""

    username: str
    password: str


class AuthResponse(ApiModel):
    """Auth response payload for POST /auth."""

    token: str


class BookingId(ApiModel):
    """List item returned by GET /booking.

    Shape:
    {
    "bookingid": 1
    }
    """

    bookingid: int
