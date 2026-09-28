# tests/unit/test_builders.py

from datetime import date, timedelta

from apiframework.models.booking import Booking
from apiframework.support.builders import BookingBuilder


def test_built_booking_is_valid() -> None:
    booking = BookingBuilder().build()

    assert isinstance(booking, Booking)
    assert booking.firstname
    assert booking.lastname
    assert booking.totalprice > 0
    assert booking.depositpaid is True
    assert booking.booking_dates.checkin >= date.today()
    assert booking.booking_dates.checkout > booking.booking_dates.checkin
    assert booking.additionalneeds == "Breakfast"


def test_default_dates_are_relative_not_hardcoded() -> None:
    booking = BookingBuilder().build()

    assert booking.booking_dates.checkin == date.today() + timedelta(days=30)
    assert booking.booking_dates.checkout == date.today() + timedelta(days=31)


def test_build_returns_unique_names() -> None:
    first = BookingBuilder().build()
    second = BookingBuilder().build()

    assert first.firstname != second.firstname
    assert first.lastname != second.lastname


def test_with_firstname_changes_firstname_only() -> None:
    builder = BookingBuilder()
    before = builder.build()
    after = builder.with_firstname("ExpectedFirst").build()

    assert after.firstname == "ExpectedFirst"
    assert after.lastname == before.lastname
    assert after.totalprice == before.totalprice


def test_with_lastname_changes_lastname_only() -> None:
    builder = BookingBuilder()
    before = builder.build()
    after = builder.with_lastname("ExpectedLast").build()

    assert after.lastname == "ExpectedLast"
    assert after.firstname == before.firstname
    assert after.totalprice == before.totalprice


def test_with_unique_name_changes_firstname_and_lastname() -> None:
    original = BookingBuilder().build()

    booking = BookingBuilder().with_unique_name("Searchable").build()

    assert booking.firstname.startswith("Searchable-First-")
    assert booking.lastname.startswith("Searchable-Last-")
    assert booking.firstname != original.firstname
    assert booking.lastname != original.lastname


def test_with_totalprice_changes_totalprice() -> None:
    booking = BookingBuilder().with_totalprice(999).build()

    assert booking.totalprice == 999


def test_with_dates_changes_checkin_and_checkout() -> None:
    checkin = date.today() + timedelta(days=10)
    checkout = date.today() + timedelta(days=12)

    booking = BookingBuilder().with_dates(checkin=checkin, checkout=checkout).build()

    assert booking.booking_dates.checkin == checkin
    assert booking.booking_dates.checkout == checkout


def test_without_deposit_changes_depositpaid() -> None:
    booking = BookingBuilder().without_deposit().build()

    assert booking.depositpaid is False


def test_without_additional_needs_changes_additionalneeds() -> None:
    booking = BookingBuilder().without_additional_needs().build()

    assert booking.additionalneeds is None


def test_build_returns_a_copy() -> None:
    builder = BookingBuilder()
    first = builder.build()
    second = builder.build()

    first.firstname = "Mutated"

    assert second.firstname != "Mutated"
