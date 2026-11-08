"""Tests for the `get_db` dependency."""

from typing import Iterator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.db import session as session_module
from app.db.session import get_db


@pytest.fixture
def isolated_session_factory(
    test_database_url: str, monkeypatch: pytest.MonkeyPatch
) -> Iterator[sessionmaker]:
    """Point get_db at the test database with a dedicated engine.

    A dedicated engine lets us inspect its pool to confirm that sessions
    give their connections back.
    """
    engine = create_engine(test_database_url)
    factory = sessionmaker(bind=engine)
    monkeypatch.setattr(session_module, "SessionLocal", factory)
    yield factory
    engine.dispose()


def test_get_db_yields_working_session(isolated_session_factory: sessionmaker) -> None:
    gen = get_db()
    db = next(gen)

    assert isinstance(db, Session)
    assert db.execute(text("SELECT 1")).scalar_one() == 1

    gen.close()


def test_get_db_closes_session_after_request(
    isolated_session_factory: sessionmaker,
) -> None:
    pool = isolated_session_factory.kw["bind"].pool
    gen = get_db()
    db = next(gen)
    db.execute(text("SELECT 1"))
    assert pool.checkedout() == 1  # the session is holding a connection

    with pytest.raises(StopIteration):
        next(gen)  # what FastAPI does when the request finishes

    assert pool.checkedout() == 0  # connection returned to the pool


def test_get_db_closes_session_when_request_fails(
    isolated_session_factory: sessionmaker,
) -> None:
    pool = isolated_session_factory.kw["bind"].pool
    gen = get_db()
    db = next(gen)
    db.execute(text("SELECT 1"))

    # FastAPI throws the route's exception into the dependency generator.
    with pytest.raises(RuntimeError):
        gen.throw(RuntimeError("route failed"))

    assert pool.checkedout() == 0
