"""Alembic migration environment.

The database URL is taken from the application's settings (DATABASE_URL),
so Alembic and the app always point at the same database. Code that runs
migrations programmatically (e.g. the test suite) can instead pass an open
connection via `config.attributes["connection"]`.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from alembic import context

import app.models  # noqa: F401  -- registers every model on Base.metadata
from app.core.config import get_settings
from app.db.base import Base

config = context.config
provided_connection: "Connection | None" = config.attributes.get("connection")

# Configure logging from alembic.ini only for CLI usage; when called from
# Python (tests), don't reset the caller's logging setup.
if config.config_file_name is not None and provided_connection is None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# compare_type: also detect column type changes during autogenerate.
CONFIGURE_OPTS = {"target_metadata": target_metadata, "compare_type": True}


def get_url() -> str:
    return get_settings().database_url


def run_migrations_offline() -> None:
    """Emit SQL to stdout instead of executing it (`alembic upgrade --sql`)."""
    context.configure(
        url=get_url(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **CONFIGURE_OPTS,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_with(connection: Connection) -> None:
    context.configure(connection=connection, **CONFIGURE_OPTS)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    if provided_connection is not None:
        run_migrations_with(provided_connection)
        return

    engine = create_engine(get_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        run_migrations_with(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
