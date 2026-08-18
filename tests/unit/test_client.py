# tests/unit/test_client.py

import httpx
import respx

from apiframework.http.client import ApiClient


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
