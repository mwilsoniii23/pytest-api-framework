# This file contains the HTTP client for the API framework.

import logging
import uuid
from types import TracebackType
from typing import Any, Self

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from apiframework.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

TRANSIENT = (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.RemoteProtocolError)


class ApiClient:
    """Thin, observable HTTP client. Retries transport faults, never status codes."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
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

    def get(self, url: str) -> httpx.Response:
        """Send a GET request."""
        return self.request("GET", url)

    def post(self, url: str) -> httpx.Response:
        """Send a POST request."""
        return self.request("POST", url)

    def put(self, url: str) -> httpx.Response:
        """Send a PUT request."""
        return self.request("PUT", url)

    def delete(self, url: str) -> httpx.Response:
        """Send a DELETE request."""
        return self.request("DELETE", url)

    def patch(self, url: str) -> httpx.Response:
        """Send a PATCH request."""
        return self.request("PATCH", url)
