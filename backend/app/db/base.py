"""Shared SQLAlchemy declarative base.

Every ORM model inherits from `Base`, so all tables end up in one
`Base.metadata` object. Alembic compares that metadata against the database
to autogenerate migrations.

This module must not import any models (that would cause circular imports);
models import `Base` from here instead. Model registration happens in
`app/models/__init__.py`.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Deterministic constraint names, so migrations are predictable and
# constraints can later be dropped/altered by name.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
