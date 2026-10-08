# tests/functional/test_booking_health.py

import pytest

from apiframework.http.client import ApiClient


@pytest.mark.integration
@pytest.mark.xfail(
    reason="/ping returns 201 Created on success; see docs/bugs-found.md #41",
    strict=True,
)
def test_health_check_returns_200() -> None:
    with ApiClient() as client:
        response = client.get("/ping")

    assert response.status_code == 200
