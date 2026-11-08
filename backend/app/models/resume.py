import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:  # imported only for type checkers; avoids a circular import
    from app.models.user import User


class Resume(Base):
    """Metadata about an uploaded resume file.

    The file bytes themselves live in external storage (added in a later
    milestone); `file_path` points to them. `file_name` is the user's original
    filename and is display-only — it is not unique and never used as an ID.
    """

    __tablename__ = "resumes"
    __table_args__ = (
        CheckConstraint("file_size >= 0", name="file_size_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,  # PostgreSQL does not index foreign keys automatically
    )
    file_name: Mapped[str] = mapped_column(String(255))
    # Location in storage; two rows must never point at the same stored file.
    file_path: Mapped[str] = mapped_column(String(1024), unique=True)
    # MIME type, e.g. "application/pdf".
    file_type: Mapped[str] = mapped_column(String(100))
    # Size in bytes. BigInteger so files > 2 GB can't overflow the column.
    file_size: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="resumes")

    def __repr__(self) -> str:
        return f"<Resume id={self.id} file_name={self.file_name!r}>"
