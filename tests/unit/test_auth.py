# tests/unit/test_auth.py

import logging

import httpx
import pytest
import respx

from apiframework.config.settings import Settings
from apiframework.http.auth import AuthProvider


@respx.mock  # type: ignore[misc]
def test_refresh_token_posts_credentials_to_auth_endpoint_and_stores_token() -> None:
    route = respx.post("/auth").mock(return_value=httpx.Response(200, json={"token": "abc123"}))
    settings = Settings(username="admin", password="password123")

    with AuthProvider(settings=settings) as auth_provider:
        token = auth_provider.refresh_token()

    assert token == "abc123"
    assert route.call_count == 1

    request = route.calls.last.request
    assert request.headers["Content-Type"] == "application/json"
    assert request.read() == b'{"username":"admin","password":"password123"}'


@respx.mock  # type: ignore[misc]
def test_get_token_returns_cached_token_without_calling_auth_endpoint() -> None:
    route = respx.post("/auth").mock(return_value=httpx.Response(200, json={"token": "abc123"}))
    settings = Settings(username="admin", password="password123")

    with AuthProvider(settings=settings) as auth_provider:
        first_token = auth_provider.get_token()
        second_token = auth_provider.get_token()

    assert first_token == "abc123"
    assert second_token == "abc123"
    assert route.call_count == 1


@respx.mock  # type: ignore[misc]
def test_refresh_token_replaces_existing_token() -> None:
    route = respx.post("/auth").mock(
        side_effect=[
            httpx.Response(200, json={"token": "old-token"}),
            httpx.Response(200, json={"token": "new-token"}),
        ]
    )
    settings = Settings(username="admin", password="password123")

    with AuthProvider(settings=settings) as auth_provider:
        old_token = auth_provider.get_token()
        new_token = auth_provider.refresh_token()

    assert old_token == "old-token"
    assert new_token == "new-token"
    assert route.call_count == 2


@respx.mock  # type: ignore[misc]
def test_refresh_token_raises_for_auth_http_error() -> None:
    respx.post("/auth").mock(return_value=httpx.Response(401, json={"reason": "Bad credentials"}))
    settings = Settings(username="admin", password="password123")

    with AuthProvider(settings=settings) as auth_provider, pytest.raises(httpx.HTTPStatusError):
        auth_provider.refresh_token()


@respx.mock  # type: ignore[misc]
def test_refresh_token_does_not_log_credentials(caplog: pytest.LogCaptureFixture) -> None:
    respx.post("/auth").mock(return_value=httpx.Response(200, json={"token": "abc123"}))
    settings = Settings(username="admin", password="password123")

    with caplog.at_level(logging.INFO), AuthProvider(settings=settings) as auth_provider:
        auth_provider.refresh_token()

    assert "admin" not in caplog.text
    assert "password123" not in caplog.text
