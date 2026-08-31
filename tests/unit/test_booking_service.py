# tests/unit/test_booking_service.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from apiframework.models.booking import (
    Booking,
    BookingDates,
    BookingId,
    CreateBookingResponse,
    PartialBooking,
)
from apiframework.services.booking_service import BookingService


@dataclass
class RecordedCall:
    method: str
    path: str
    kwargs: dict[str, Any]


class StubResponse:
    def __init__(self, payload: Any = None) -> None:
        self._payload = payload
        self.raise_for_status_call_count = 0

    def raise_for_status(self) -> None:
        self.raise_for_status_call_count += 1

    def json(self) -> Any:
        return self._payload


class StubApiClient:
    def __init__(self) -> None:
        self.calls: list[RecordedCall] = []
        self.next_response = StubResponse()

    def get(self, path: str, **kwargs: Any) -> StubResponse:
        self.calls.append(RecordedCall(method="GET", path=path, kwargs=kwargs))
        return self.next_response

    def post(self, path: str, **kwargs: Any) -> StubResponse:
        self.calls.append(RecordedCall(method="POST", path=path, kwargs=kwargs))
        return self.next_response

    def put(self, path: str, **kwargs: Any) -> StubResponse:
        self.calls.append(RecordedCall(method="PUT", path=path, kwargs=kwargs))
        return self.next_response

    def patch(self, path: str, **kwargs: Any) -> StubResponse:
        self.calls.append(RecordedCall(method="PATCH", path=path, kwargs=kwargs))
        return self.next_response

    def delete(self, path: str, **kwargs: Any) -> StubResponse:
        self.calls.append(RecordedCall(method="DELETE", path=path, kwargs=kwargs))
        return self.next_response


def make_booking() -> Booking:
    return Booking(
        firstname="Jim",
        lastname="Brown",
        totalprice=111,
        depositpaid=True,
        booking_dates=BookingDates(
            checkin=date(2026, 1, 1),
            checkout=date(2026, 1, 2),
        ),
        additionalneeds="Breakfast",
    )


def test_list_booking_ids_returns_typed_booking_id_models() -> None:
    client = StubApiClient()
    client.next_response = StubResponse(
        [
            BookingId(bookingid=1).model_dump(mode="json"),
            BookingId(bookingid=2).model_dump(mode="json"),
        ]
    )

    service = BookingService(api_client=client)

    booking_ids = service.list_booking_ids()

    assert booking_ids == [BookingId(bookingid=1), BookingId(bookingid=2)]
    assert "headers" not in client.calls[0].kwargs


def test_list_booking_ids_sends_optional_query_params() -> None:
    client = StubApiClient()
    client.next_response = StubResponse([BookingId(bookingid=1).model_dump(mode="json")])

    service = BookingService(api_client=client)

    booking_ids = service.list_booking_ids(
        firstname="Jim",
        lastname="Brown",
        checkin=date(2026, 1, 1),
        checkout=date(2026, 1, 2),
    )

    assert booking_ids == [BookingId(bookingid=1)]
    assert client.calls == [
        RecordedCall(
            method="GET",
            path="/booking",
            kwargs={
                "params": {
                    "firstname": "Jim",
                    "lastname": "Brown",
                    "checkin": "2026-01-01",
                    "checkout": "2026-01-02",
                }
            },
        )
    ]
    assert "headers" not in client.calls[0].kwargs


def test_get_booking_returns_typed_booking_model() -> None:
    client = StubApiClient()
    expected_booking = make_booking()
    client.next_response = StubResponse(expected_booking.model_dump(mode="json", by_alias=True))

    service = BookingService(api_client=client)

    booking = service.get_booking(1)

    assert booking == expected_booking
    assert client.calls == [
        RecordedCall(
            method="GET",
            path="/booking/1",
            kwargs={},
        )
    ]
    assert client.next_response.raise_for_status_call_count == 1
    assert "headers" not in client.calls[0].kwargs


def test_create_booking_returns_typed_create_booking_response() -> None:
    client = StubApiClient()
    booking = make_booking()
    expected_response = CreateBookingResponse(bookingid=1, booking=booking)
    client.next_response = StubResponse(expected_response.model_dump(mode="json", by_alias=True))

    service = BookingService(api_client=client)

    response = service.create_booking(booking)

    assert response == expected_response
    assert client.calls == [
        RecordedCall(
            method="POST",
            path="/booking",
            kwargs={
                "headers": {"Content-Type": "application/json"},
                "json": booking.model_dump(mode="json", by_alias=True),
            },
        )
    ]
    assert "Cookie" not in client.calls[0].kwargs["headers"]


def test_update_booking_returns_typed_booking_model() -> None:
    client = StubApiClient()
    booking = make_booking()
    client.next_response = StubResponse(booking.model_dump(mode="json", by_alias=True))

    service = BookingService(api_client=client)

    updated_booking = service.update_booking(1, booking)

    assert updated_booking == booking
    assert client.calls == [
        RecordedCall(
            method="PUT",
            path="/booking/1",
            kwargs={
                "headers": {"Accept": "application/json", "Content-Type": "application/json"},
                "json": booking.model_dump(mode="json", by_alias=True),
            },
        )
    ]


def test_partial_update_booking_returns_typed_booking_model() -> None:
    client = StubApiClient()
    expected_booking = make_booking()
    partial_booking = PartialBooking(firstname="Jim")
    client.next_response = StubResponse(expected_booking.model_dump(mode="json", by_alias=True))

    service = BookingService(api_client=client)

    booking = service.partial_update_booking(1, partial_booking)

    assert booking == expected_booking
    assert client.calls == [
        RecordedCall(
            method="PATCH",
            path="/booking/1",
            kwargs={
                "headers": {"Accept": "application/json", "Content-Type": "application/json"},
                "json": {"firstname": "Jim"},
            },
        )
    ]


def test_delete_booking_raises_for_status_and_returns_none() -> None:
    client = StubApiClient()

    service = BookingService(api_client=client)

    result = service.delete_booking(1)

    assert result is None
    assert client.calls == [
        RecordedCall(
            method="DELETE",
            path="/booking/1",
            kwargs={"headers": {"Accept": "application/json"}},
        )
    ]
    assert client.next_response.raise_for_status_call_count == 1
