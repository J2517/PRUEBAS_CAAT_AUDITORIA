import pytest

from caat.config import Config


@pytest.fixture
def cfg() -> Config:
    return Config()
