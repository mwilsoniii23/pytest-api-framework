# /src/apiframework/http/auth.py

import logging
from types import TracebackType
from typing import Self

import httpx

from apiframework.config.settings import Settings, get_settings
from apiframework.models.booking import AuthRequest, AuthResponse

logger = logging.getLogger(__name__)


class AuthProvider:
    """Fetches and stores API auth tokens.

    The provider owns credential handling so ApiClient does not need to know
    where credentials come from or how auth payloads are constructed.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._token: str | None = None
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
        self.close()

    @property
    def token(self) -> str | None:
        """Return the currently cached token, if one exists."""
        return self._token

    def close(self) -> None:
        """Close the HTTPX client."""
        self._client.close()

    def get_token(self) -> str:
        """Return the cached token, fetching one first if necessary."""
        if self._token is None:
            return self.refresh_token()

        return self._token

    def refresh_token(self) -> str:
        """Fetch a new token from POST /auth and cache it."""
        logger.info("Requesting new auth token")

        auth_request = AuthRequest(
            username=self._settings.username,
            password=self._settings.password,
        )

        response = self._client.post(
            "/auth",
            headers={"Content-Type": "application/json"},
            json=auth_request.model_dump(mode="json"),
        )
        response.raise_for_status()

        auth_response = AuthResponse.model_validate(response.json())
        self._token = auth_response.token

        logger.info("Auth token refreshed")

        return self._token
