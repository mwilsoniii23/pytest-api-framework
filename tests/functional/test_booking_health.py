# tests/functional/test_booking_health.py

import pytest

from apiframework.http.client import ApiClient


@pytest.mark.integration
def test_health_check_returns_200() -> None:
    with ApiClient() as client:
        response = client.get("/ping")

    assert response.status_code == 200
