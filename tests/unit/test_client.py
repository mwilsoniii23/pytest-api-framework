# tests/unit/test_client.py

import httpx
import respx

from apiframework.http.client import ApiClient


class StubAuthProvider:
    def __init__(self) -> None:
        self.get_token_call_count = 0
        self.refresh_token_call_count = 0
        self.close_call_count = 0

    def get_token(self) -> str:
        self.get_token_call_count += 1
        return "cached-token"

    def refresh_token(self) -> str:
        self.refresh_token_call_count += 1
        return "refreshed-token"

    def close(self) -> None:
        self.close_call_count += 1


@respx.mock  # type: ignore[misc]
def test_retries_transient_error() -> None:
    route = respx.get("/booking").mock(
        side_effect=[httpx.ConnectError("boom"), httpx.Response(200, json=[])]
    )

    with ApiClient() as client:
        response = client.get("/booking")

    assert response.status_code == 200
    assert route.call_count == 2


@respx.mock  # type: ignore[misc]
def test_does_not_retry_server_error() -> None:
    route = respx.get("/booking").mock(return_value=httpx.Response(500))

    with ApiClient() as client:
        response = client.get("/booking")

    assert response.status_code == 500
    assert route.call_count == 1


@respx.mock  # type: ignore[misc]
def test_put_sends_cached_token_in_cookie_header() -> None:
    auth_provider = StubAuthProvider()
    route = respx.put("/booking/1").mock(return_value=httpx.Response(200, json={}))

    with ApiClient(auth_provider=auth_provider) as client:
        response = client.put("/booking/1", json={"firstname": "Jim"})

    assert response.status_code == 200
    assert auth_provider.get_token_call_count == 1
    assert auth_provider.refresh_token_call_count == 0
    assert route.calls.last.request.headers["Cookie"] == "token=cached-token"


@respx.mock  # type: ignore[misc]
def test_patch_sends_cached_token_in_cookie_header() -> None:
    auth_provider = StubAuthProvider()
    route = respx.patch("booking/1").mock(return_value=httpx.Response(200, json={}))

    with ApiClient(auth_provider=auth_provider) as client:
        response = client.patch("/booking/1", json={"firstname": "Jane"})

    assert response.status_code == 200
    assert auth_provider.get_token_call_count == 1
    assert auth_provider.refresh_token_call_count == 0
    assert route.call_count == 1
    assert route.calls.last.request.headers["Cookie"] == "token=cached-token"
