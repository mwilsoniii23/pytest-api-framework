# tests/unit/test_booking_service.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx
import pytest

from apiframework.models.booking import (
    Booking,
    BookingDates,
    BookingId,
    CreateBookingResponse,
    PartialBooking,
)
from apiframework.services.booking_service import BookingApiError, BookingService


@dataclass
class RecordedCall:
    method: str
    path: str
    kwargs: dict[str, Any]


class StubResponse:
    def __init__(self, payload: Any = None, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)
        self.raise_for_status_call_count = 0

    def raise_for_status(self) -> None:
        self.raise_for_status_call_count += 1

        if self.status_code >= 400:
            request = httpx.Request("GET", "https://example.test/booking")
            response = httpx.Response(
                status_code=self.status_code,
                request=request,
                text=self.text,
            )
            raise httpx.HTTPStatusError(
                message=f"Error response {self.status_code}",
                request=request,
                response=response,
            )

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


@pytest.fixture
def stub_client() -> StubApiClient:
    return StubApiClient()


@pytest.fixture
def stubbed_booking_service(stub_client: StubApiClient) -> BookingService:
    return BookingService(api_client=stub_client)


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


def test_list_booking_ids_returns_typed_booking_id_models(
    stubbed_booking_service: BookingService,
    stub_client: StubApiClient,
) -> None:
    stub_client.next_response = StubResponse(
        [
            BookingId(bookingid=1).model_dump(mode="json"),
            BookingId(bookingid=2).model_dump(mode="json"),
        ]
    )

    booking_ids = stubbed_booking_service.list_booking_ids()

    assert booking_ids == [BookingId(bookingid=1), BookingId(bookingid=2)]
    assert stub_client.calls == [
        RecordedCall(
            method="GET",
            path="/booking",
            kwargs={"params": None},
        )
    ]
    assert stub_client.next_response.raise_for_status_call_count == 1
    assert "headers" not in stub_client.calls[0].kwargs


def test_list_booking_ids_sends_optional_query_params(
    stubbed_booking_service: BookingService,
    stub_client: StubApiClient,
) -> None:
    stub_client.next_response = StubResponse([BookingId(bookingid=1).model_dump(mode="json")])

    booking_ids = stubbed_booking_service.list_booking_ids(
        firstname="Jim",
        lastname="Brown",
        checkin=date(2026, 1, 1),
        checkout=date(2026, 1, 2),
    )

    assert booking_ids == [BookingId(bookingid=1)]
    assert stub_client.calls == [
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
    assert "headers" not in stub_client.calls[0].kwargs


def test_get_booking_returns_typed_booking_model(
    stubbed_booking_service: BookingService,
    stub_client: StubApiClient,
) -> None:
    expected_booking = make_booking()
    stub_client.next_response = StubResponse(
        expected_booking.model_dump(mode="json", by_alias=True)
    )

    booking = stubbed_booking_service.get_booking(1)

    assert booking == expected_booking
    assert stub_client.calls == [
        RecordedCall(
            method="GET",
            path="/booking/1",
            kwargs={},
        )
    ]
    assert stub_client.next_response.raise_for_status_call_count == 1
    assert "headers" not in stub_client.calls[0].kwargs


def test_create_booking_returns_typed_create_booking_response(
    stubbed_booking_service: BookingService,
    stub_client: StubApiClient,
) -> None:
    booking = make_booking()
    expected_response = CreateBookingResponse(bookingid=1, booking=booking)
    stub_client.next_response = StubResponse(
        expected_response.model_dump(mode="json", by_alias=True)
    )

    response = stubbed_booking_service.create_booking(booking)

    assert response == expected_response
    assert stub_client.calls == [
        RecordedCall(
            method="POST",
            path="/booking",
            kwargs={
                "headers": {"Content-Type": "application/json"},
                "json": booking.model_dump(mode="json", by_alias=True),
            },
        )
    ]
    assert "Cookie" not in stub_client.calls[0].kwargs["headers"]


def test_update_booking_returns_typed_booking_model(
    stubbed_booking_service: BookingService,
    stub_client: StubApiClient,
) -> None:
    booking = make_booking()
    stub_client.next_response = StubResponse(booking.model_dump(mode="json", by_alias=True))

    updated_booking = stubbed_booking_service.update_booking(1, booking)

    assert updated_booking == booking
    assert stub_client.calls == [
        RecordedCall(
            method="PUT",
            path="/booking/1",
            kwargs={
                "headers": {"Accept": "application/json", "Content-Type": "application/json"},
                "json": booking.model_dump(mode="json", by_alias=True),
            },
        )
    ]


def test_partial_update_booking_returns_typed_booking_model(
    stubbed_booking_service: BookingService,
    stub_client: StubApiClient,
) -> None:
    expected_booking = make_booking()
    partial_booking = PartialBooking(firstname="Jim")
    stub_client.next_response = StubResponse(
        expected_booking.model_dump(mode="json", by_alias=True)
    )

    booking = stubbed_booking_service.partial_update_booking(1, partial_booking)

    assert booking == expected_booking
    assert stub_client.calls == [
        RecordedCall(
            method="PATCH",
            path="/booking/1",
            kwargs={
                "headers": {"Accept": "application/json", "Content-Type": "application/json"},
                "json": {"firstname": "Jim"},
            },
        )
    ]


def test_delete_booking_raises_for_status_and_returns_none(
    stubbed_booking_service: BookingService,
    stub_client: StubApiClient,
) -> None:
    result = stubbed_booking_service.delete_booking(1)

    assert result is None
    assert stub_client.calls == [
        RecordedCall(
            method="DELETE",
            path="/booking/1",
            kwargs={"headers": {"Accept": "application/json"}},
        )
    ]
    assert stub_client.next_response.raise_for_status_call_count == 1


def test_get_booking_raises_booking_api_error_with_response(
    stubbed_booking_service: BookingService,
    stub_client: StubApiClient,
) -> None:
    stub_client.next_response = StubResponse("Not Found", status_code=404)

    with pytest.raises(BookingApiError) as exc_info:
        stubbed_booking_service.get_booking(999999)

    assert exc_info.value.response.status_code == 404
    assert exc_info.value.response.text == "Not Found"
    assert stub_client.next_response.raise_for_status_call_count == 1
