# /src/apiframework/services/booking_service.py

from datetime import date
from types import TracebackType
from typing import Any, Protocol, Self, cast

import httpx

from apiframework.http.client import ApiClient
from apiframework.models.booking import Booking, BookingId, CreateBookingResponse, PartialBooking


class HttpClient(Protocol):
    """HTTP behavior required by BookingService"""

    def get(self, url: str, **kwargs: Any) -> httpx.Response: ...

    def post(self, url: str, **kwargs: Any) -> httpx.Response: ...

    def put(self, url: str, **kwargs: Any) -> httpx.Response: ...

    def patch(self, url: str, **kwargs: Any) -> httpx.Response: ...

    def delete(self, url: str, **kwargs: Any) -> httpx.Response: ...


class BookingApiError(Exception):
    """Raised when the Booking API returns an unsuccessful response."""

    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        super().__init__(
            f"Booking API request failed with status: {response.status_code}: {response.text}"
        )


class BookingService:
    """Typed service layer for Restful Booker booking operations."""

    def __init__(self, api_client: HttpClient | None = None) -> None:
        self._client = api_client or ApiClient()
        self._owns_client = api_client is None

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close owned HTTP resources."""
        if self._owns_client:
            cast(ApiClient, self._client).__exit__(None, None, None)

    def list_booking_ids(
        self,
        *,
        firstname: str | None = None,
        lastname: str | None = None,
        checkin: date | None = None,
        checkout: date | None = None,
    ) -> list[BookingId]:
        """Return booking IDs from GET /booking.

        Supports the optional API filters:
        firstname, lastname, checkin, checkout
        """
        params = self._build_booking_id_query_params(
            firstname=firstname,
            lastname=lastname,
            checkin=checkin,
            checkout=checkout,
        )

        response = self._client.get("/booking", params=params or None)
        self._raise_for_status(response)

        return [BookingId.model_validate(item) for item in response.json()]

    def get_booking(self, booking_id: int) -> Booking:
        """Return a booking from GET /booking/{id}"""
        response = self._client.get(f"/booking/{booking_id}")
        self._raise_for_status(response)

        return Booking.model_validate(response.json())

    def create_booking(self, booking: Booking) -> CreateBookingResponse:
        """Create a booking from POST /booking"""
        response = self._client.post(
            "/booking",
            headers={"Content-Type": "application/json"},
            json=booking.model_dump(mode="json", by_alias=True),
        )
        self._raise_for_status(response)

        return CreateBookingResponse.model_validate(response.json())

    def update_booking(self, booking_id: int, booking: Booking) -> Booking:
        """Update a booking from PUT /booking/{id}"""
        response = self._client.put(
            f"/booking/{booking_id}",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json=booking.model_dump(mode="json", by_alias=True),
        )
        self._raise_for_status(response)

        return Booking.model_validate(response.json())

    def partial_update_booking(self, booking_id: int, booking: PartialBooking) -> Booking:
        """Partially update a booking from PATCH /booking/{id}"""
        response = self._client.patch(
            f"/booking/{booking_id}",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json=booking.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        self._raise_for_status(response)

        return Booking.model_validate(response.json())

    def delete_booking(self, booking_id: int) -> None:
        """Delete a booking from DELETE /booking/{id}"""
        response = self._client.delete(
            f"/booking/{booking_id}",
            headers={"Accept": "application/json"},
        )
        self._raise_for_status(response)

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise BookingApiError(response) from exc

    @staticmethod
    def _build_booking_id_query_params(
        *,
        firstname: str | None,
        lastname: str | None,
        checkin: date | None,
        checkout: date | None,
    ) -> dict[str, str]:
        params: dict[str, str] = {}

        if firstname is not None:
            params["firstname"] = firstname
        if lastname is not None:
            params["lastname"] = lastname
        if checkin is not None:
            params["checkin"] = checkin.isoformat()
        if checkout is not None:
            params["checkout"] = checkout.isoformat()

        return params
