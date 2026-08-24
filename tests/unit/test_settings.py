# test/unit/test_settings.py
# defaults load correctly
# an env var overrides a default (use pytest's monkeypatch fixture);
# an out-of-range timeout_seconds raises ValidationError;
# an unknown BOOKER_* variable raises.

import os

import pytest
from pydantic import ValidationError
from pytest import MonkeyPatch

from apiframework.config.settings import Settings

BOOKER_ENV_PREFIX = "BOOKER_"


@pytest.fixture(autouse=True)
def clean_booker_env(monkeypatch: MonkeyPatch) -> None:
    """Keep tests isolated from the developer/CI environment."""
    for key in list(os.environ):
        if key.startswith(BOOKER_ENV_PREFIX):
            monkeypatch.delenv(key)


def test_defaults_load_correctly() -> None:
    settings = Settings()

    assert str(settings.base_url) == "https://restful-booker.herokuapp.com/"
    assert settings.username == "admin"
    assert settings.password == "password123"
    assert settings.timeout_seconds == 10.0
    # assert settings.max_retries == 3


def test_env_var_overrides_default(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("BOOKER_TIMEOUT_SECONDS", "25.5")

    settings = Settings()

    assert settings.timeout_seconds == 25.5


@pytest.mark.parametrize("timeout_seconds", ["0", "-1", "60.1"])
def test_out_of_range_timeout_seconds_raises_validation_error(
    monkeypatch: MonkeyPatch, timeout_seconds: str
) -> None:
    monkeypatch.setenv("BOOKER_TIMEOUT_SECONDS", timeout_seconds)

    with pytest.raises(ValidationError):
        Settings()


def test_known_booker_variable_does_not_raise_validation_error(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("BOOKER_USERNAME", "test_admin")

    settings = Settings()

    assert settings.username == "test_admin"


def test_unknown_booker_variable_raises_validation_error(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("BOOKER_UNKNOWN_SETTING", "surprise")

    with pytest.raises(ValidationError):
        Settings()
