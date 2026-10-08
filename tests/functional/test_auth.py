# tests/functional/test_auth.py


import pytest

from apiframework.http.client import ApiClient


@pytest.mark.integration
def test_auth_with_valid_credentials_returns_token() -> None:
    payload = {
        "username": "admin",
        "password": "password123",
    }

    with ApiClient() as client:
        response = client.post("/auth", json=payload)

    assert response.status_code == 200
    assert isinstance(response.json()["token"], str)
    assert response.json()["token"]


@pytest.mark.integration
@pytest.mark.xfail(
    reason="Auth endpoint returns 200 OK when request has invalid credentials; "
    "see docs/bugs-found.md #45"
)
def test_auth_with_invalid_credentials_is_rejected() -> None:
    payload = {
        "username": "invalid",
        "password": "invalid",
    }

    with ApiClient() as client:
        response = client.post("/auth", json=payload)

    assert response.status_code in {400, 401, 403, 422}


@pytest.mark.integration
@pytest.mark.xfail(
    reason="Auth endpoint returns 200 OK when request missing required payload; "
    "see docs/bugs-found.md #46"
)
def test_auth_without_payload_is_rejected() -> None:
    with ApiClient() as client:
        response = client.request(
            "POST",
            "/auth",
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code in {400, 401, 403, 422}
