# /src/apiframework/http/factory.py

import httpx

from apiframework.config.settings import Settings


def build_http_client(settings: Settings) -> httpx.Client:
    """Build a configured HTTPX client for the API framework."""
    return httpx.Client(
        base_url=str(settings.base_url),
        timeout=httpx.Timeout(
            connect=5.0,
            read=settings.timeout_seconds,
            write=5.0,
            pool=5.0,
        ),
        follow_redirects=False,
    )
