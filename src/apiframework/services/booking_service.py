# /src/apiframework/services/booking_service.py

from datetime import date
from types import TracebackType
from typing import Self

from apiframework.http.client import ApiClient
from apiframework.models.booking import Booking, BookingId, CreateBookingResponse, PartialBooking


class BookingService:
    """Typed service layer for Restful Booker booking operations."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
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
            self._client.__exit__(None, None, None)

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
        response.raise_for_status()

        return [BookingId.model_validate(item) for item in response.json()]

    def get_booking(self, booking_id: int) -> Booking:
        """Return a booking from GET /booking/{id}"""
        response = self._client.get(f"/booking/{booking_id}")
        response.raise_for_status()

        return Booking.model_validate(response.json())

    def create_booking(self, booking: Booking) -> CreateBookingResponse:
        """Create a booking from POST /booking"""
        response = self._client.post(
            "/booking",
            headers={"Content-Type": "application/json"},
            json=booking.model_dump(mode="json", by_alias=True),
        )
        response.raise_for_status()

        return CreateBookingResponse.model_validate(response.json())

    def update_booking(self, booking_id: int, booking: Booking) -> Booking:
        """Update a booking from PUT /booking/{id}"""
        response = self._client.put(
            f"/booking/{booking_id}",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json=booking.model_dump(mode="json", by_alias=True),
        )
        response.raise_for_status()

        return Booking.model_validate(response.json())

    def partial_update_booking(self, booking_id: int, booking: PartialBooking) -> Booking:
        """Partially update a booking from PATCH /booking/{id}"""
        response = self._client.patch(
            f"/booking/{booking_id}",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json=booking.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        response.raise_for_status()

        return Booking.model_validate(response.json())

    def delete_booking(self, booking_id: int) -> None:
        """Delete a booking from DELETE /booking/{id}"""
        response = self._client.delete(
            f"/booking/{booking_id}",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()

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


def list_booking_ids(
    *,
    firstname: str | None = None,
    lastname: str | None = None,
    checkin: date | None = None,
    checkout: date | None = None,
) -> list[BookingId]:
    """Return booking IDs from GET /booking."""
    with BookingService() as service:
        return service.list_booking_ids(
            firstname=firstname, lastname=lastname, checkin=checkin, checkout=checkout
        )


def get_booking(booking_id: int) -> Booking:
    """Return a booking from GET /booking/{id}"""
    with BookingService() as service:
        return service.get_booking(booking_id)


def create_booking(booking: Booking) -> CreateBookingResponse:
    """Create a booking from POST /booking"""
    with BookingService() as service:
        return service.create_booking(booking)


def update_booking(booking_id: int, booking: Booking) -> Booking:
    """Update a booking from PUT /booking/{id}"""
    with BookingService() as service:
        return service.update_booking(booking_id, booking)


def partial_update_booking(booking_id: int, booking: PartialBooking) -> Booking:
    """Partially update a booking from PATCH /booking/{id}"""
    with BookingService() as service:
        return service.partial_update_booking(booking_id, booking)


def delete_booking(booking_id: int) -> None:
    """Delete a booking from DELETE /booking/{id}"""
    with BookingService() as service:
        return service.delete_booking(booking_id)
