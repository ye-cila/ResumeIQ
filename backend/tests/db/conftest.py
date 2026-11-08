"""Fixtures for tests that need a real PostgreSQL database.

Safety rules:
- Tests only ever connect to TEST_DATABASE_URL, never DATABASE_URL.
- The test database name must end in `_test` and differ from the dev
  database, otherwise the tests refuse to run.

The schema is built with Alembic (not `create_all`), so these tests also
verify that the migrations work. Each test runs inside a transaction that is
rolled back afterwards, so tests never see each other's data.
"""

from pathlib import Path
from typing import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import get_settings

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _safe_test_database_url() -> str:
    settings = get_settings()
    url = settings.test_database_url
    if not url:
        pytest.skip("TEST_DATABASE_URL is not set; skipping database tests")

    test_db = make_url(url).database or ""
    dev_db = make_url(settings.database_url).database
    if not test_db.endswith("_test") or test_db == dev_db:
        pytest.exit(
            f"Refusing to run DB tests against {test_db!r}: the test database "
            "name must end in '_test' and differ from DATABASE_URL.",
            returncode=1,
        )
    return url


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return _safe_test_database_url()


@pytest.fixture(scope="session")
def db_engine(test_database_url: str) -> Iterator[Engine]:
    engine = create_engine(test_database_url)

    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        # Start from an empty schema, then apply every migration.
        command.downgrade(alembic_cfg, "base")
        command.upgrade(alembic_cfg, "head")

    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Iterator[Session]:
    """A Session whose work is always rolled back at the end of the test.

    `join_transaction_mode="create_savepoint"` makes `session.commit()` and
    `session.rollback()` inside a test operate on a SAVEPOINT, so the outer
    transaction (and thus all test data) can still be rolled back.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
