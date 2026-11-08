from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


def get_test_settings() -> Settings:
    # _env_file=None: don't let a developer's local .env affect test results.
    return Settings(_env_file=None, environment="testing")


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_settings] = get_test_settings
    with TestClient(app) as test_client:
        yield test_client
