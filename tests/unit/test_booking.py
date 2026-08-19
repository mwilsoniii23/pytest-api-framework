# tests/unit/test_booking.py

from datetime import date

import pytest
from pydantic import ValidationError

from apiframework.models.booking import (
    AuthResponse,
    Booking,
    BookingDates,
    BookingId,
    CreateBookingResponse,
)


def test_booking_dates_parses_iso_strings_to_date_objects() -> None:
    booking_dates = BookingDates(checkin=date(2023, 1, 1), checkout=date(2023, 1, 2))

    assert booking_dates.checkin == date(2023, 1, 1)
    assert booking_dates.checkout == date(2023, 1, 2)
    assert isinstance(booking_dates.checkin, date)
    assert isinstance(booking_dates.checkout, date)


def test_booking_accepts_pythonic_booking_dates_field_name() -> None:
    booking = Booking(
        firstname="Jim",
        lastname="Brown",
        totalprice=111,
        depositpaid=True,
        booking_dates=BookingDates(checkin="2023-01-01", checkout="2023-01-02"),
        additionalneeds="Breakfast",
    )

    assert booking.firstname == "Jim"
    assert booking.lastname == "Brown"
    assert booking.totalprice == 111
    assert booking.depositpaid is True
    assert booking.booking_dates.checkin == date(2023, 1, 1)
    assert booking.booking_dates.checkout == date(2023, 1, 2)
    assert booking.additionalneeds == "Breakfast"


def test_booking_accepts_api_alias_bookingdates_field_name() -> None:
    booking = Booking.model_validate(
        {
            "firstname": "Jim",
            "lastname": "Brown",
            "totalprice": 111,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2023-01-01",
                "checkout": "2023-01-02",
            },
            "additionalneeds": "Breakfast",
        }
    )

    assert booking.booking_dates.checkin == BookingDates(
        checkin=date(2023, 1, 1),
        checkout=date(2023, 1, 2),
    )


def test_booking_serialized_with_api_alias() -> None:
    booking = Booking(
        firstname="Jim",
        lastname="Brown",
        totalprice=111,
        depositpaid=True,
        bookingdates=BookingDates(checkin=date(2023, 1, 1), checkout=date(2023, 1, 2)),
        additionalneeds="Breakfast",
    )

    payload = booking.model_dump(mode="json", by_alias=True)

    assert payload == {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2023-01-01",
            "checkout": "2023-01-02",
        },
        "additionalneeds": "Breakfast",
    }


def test_booking_additional_is_optional_and_can_be_excluded_when_none() -> None:
    booking = Booking(
        firstname="Jim",
        lastname="Brown",
        totalprice=111,
        depositpaid=True,
        bookingdates=BookingDates(
            checkin=date(2023, 1, 1),
            checkout=date(2023, 1, 2),
        ),
    )

    assert booking.additionalneeds is None

    payload = booking.model_dump(mode="json", by_alias=True, exclude_none=True)

    assert payload == {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2023-01-01",
            "checkout": "2023-01-02",
        },
    }


def test_create_booking_response_models_post_booking_envelope() -> None:
    response = CreateBookingResponse.model_validate(
        {
            "bookingid": 1,
            "booking": {
                "firstname": "Jim",
                "lastname": "Brown",
                "totalprice": 111,
                "depositpaid": True,
                "bookingdates": {
                    "checkin": "2023-01-01",
                    "checkout": "2023-01-02",
                },
                "additionalneeds": "Breakfast",
            },
        }
    )

    assert response.bookingid == 1
    assert response.booking.firstname == "Jim"
    assert response.booking.booking_dates.checkin == date(2023, 1, 1)


def test_get_booking_response_is_booking_directly_without_envelope() -> None:
    booking = Booking.model_validate(
        {
            "firstname": "Jim",
            "lastname": "Brown",
            "totalprice": 111,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2023-01-01",
                "checkout": "2023-01-02",
            },
            "additionalneeds": "Breakfast",
        }
    )

    assert booking.firstname == "Jim"
    assert booking.booking_dates.checkout == date(2023, 1, 2)


def test_auth_response_models_token() -> None:
    auth_response = AuthResponse.model_validate({"token": "abc123"})

    assert auth_response.token == "abc123"


def test_booking_id_models_get_booking_list_item() -> None:
    booking_id = BookingId.model_validate({"bookingid": 1})

    assert booking_id.bookingid == 1


@pytest.mark.parametrize(
    "payload",
    [
        {
            "checkin": "not-a-date",
            "checkout": "2023-01-02",
        },
        {
            "checkin": "2023-01-01",
            "checkout": "not-a-date",
        },
    ],
)
def test_booking_dates_rejects_invalid_date_strings(payload: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        BookingDates.model_validate(payload)
