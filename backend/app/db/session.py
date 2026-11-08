"""Database engine, session factory, and the `get_db` FastAPI dependency.

The engine (and its connection pool) is created once when this module is
imported and shared by the whole process. Each request gets its own short-lived
Session from `SessionLocal`, which borrows a pooled connection.
"""

from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# create_engine does not connect yet; connections are opened lazily on first use.
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,  # transparently replace connections the server dropped
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    # Keep loaded attributes usable after commit (e.g. to build a response)
    # without triggering an extra SELECT.
    expire_on_commit=False,
)


def get_db() -> Iterator[Session]:
    """Yield a database session for one request and always close it.

    Usage in a route:

        def endpoint(db: Session = Depends(get_db)): ...

    Routes/services are responsible for calling `db.commit()`. Closing the
    session without committing rolls back any uncommitted work.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
