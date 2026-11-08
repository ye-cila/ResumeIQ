"""Model registry.

Importing `app.models` imports every model module, which registers each table
on `Base.metadata`. Alembic's env.py imports this package so autogenerate sees
all tables. When you add a model, import it here.
"""

from app.models.resume import Resume
from app.models.user import User

__all__ = ["Resume", "User"]
