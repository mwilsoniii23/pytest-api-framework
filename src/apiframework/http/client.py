# This file contains the HTTP client for the API framework.

import logging
import uuid
from types import TracebackType
from typing import Any, Protocol, Self

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from apiframework.config.settings import Settings, get_settings
from apiframework.http.auth import AuthProvider

logger = logging.getLogger(__name__)

TRANSIENT = (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.RemoteProtocolError)
AUTH_FAILURE_STATUSES = {401, 403}


class TokenProvider(Protocol):
    """Auth behavior required by ApiClient"""

    def get_token(self) -> str:
        """Return an existing token or fetch one"""
        ...

    def refresh_token(self) -> str:
        """Force-fetch and return a new token"""
        ...

    def close(self) -> None:
        """Release auth provider resources"""
        ...


class ApiClient:
    """Thin, observable HTTP client. Retries transport faults, never status codes."""

    def __init__(
        self,
        settings: Settings | None = None,
        auth_provider: TokenProvider | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._auth_provider = auth_provider or AuthProvider(self._settings)
        self._client = httpx.Client(
            base_url=str(self._settings.base_url),
            timeout=httpx.Timeout(
                connect=5.0,
                read=self._settings.timeout_seconds,
                write=5.0,
                pool=5.0,
            ),
            follow_redirects=False,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._client.close()
        self._auth_provider.close()

    @retry(  # type: ignore[misc]
        retry=retry_if_exception_type(TRANSIENT),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, max=4),
        reraise=True,
    )
    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        correlation_id = uuid.uuid4().hex[:12]
        headers = {**kwargs.pop("headers", {}), "X-Correlation-ID": correlation_id}
        logger.info("-> %s %s [%s]", method, url, correlation_id)
        response = self._client.request(method, url, headers=headers, **kwargs)
        logger.info(
            "<- %s %s [%s] %.0fms",
            response.status_code,
            url,
            correlation_id,
            response.elapsed.total_seconds() * 1000,
        )

        return response

    def authenticated_request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Send an authenticated request.

        Tries the cached token first. If the API rejects it, refreshes the token
        and retries the request once.
        """
        response = self._request_with_token(
            method=method,
            url=url,
            token=self._auth_provider.get_token(),
            **kwargs,
        )

        if response.status_code not in AUTH_FAILURE_STATUSES:
            return response

        logger.info("Auth token rejected with %s; refreshing token", response.status_code)

        return self._request_with_token(
            method=method,
            url=url,
            token=self._auth_provider.refresh_token(),
            **kwargs,
        )

    def _request_with_token(
        self, method: str, url: str, token: str, **kwargs: Any
    ) -> httpx.Response:
        headers = {
            **kwargs.pop("headers", {}),
            "Cookie": f"token={token}",
        }
        return self.request(method, url, headers=headers, **kwargs)

    def get(self, url: str, **kwargs: str) -> httpx.Response:
        """Send a GET request."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: str) -> httpx.Response:
        """Send a POST request."""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: str) -> httpx.Response:
        """Send an authenticated PUT request."""
        return self.authenticated_request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: str) -> httpx.Response:
        """Send an authenticated DELETE request."""
        return self.authenticated_request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs: str) -> httpx.Response:
        """Send a PATCH request."""
        return self.request("PATCH", url, **kwargs)
