# tests/functional/test_get_booking.py

import pytest

from apiframework.http.client import ApiClient


@pytest.mark.integration
@pytest.mark.xfail(reason="Empty checkout param returns 500; see bugs-found.md #46")
def test_empty_checkout_param_is_rejected() -> None:
    with ApiClient() as client:
        response = client.get("/booking", params={"checkout": ""})
    assert response.status_code == 400
