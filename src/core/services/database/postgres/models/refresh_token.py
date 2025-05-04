from __future__ import annotations
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship
    )
from sqlalchemy import func, String, Integer, ForeignKey
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from src.core.services.database.postgres.models.base import Base, int_pk, created_at


if TYPE_CHECKING:
    from src.core.services.database.postgres.models.user import UserModel  # Path to your UserModel

class RefreshTokenModel(Base):
    """SQLAlchemy model for persistent storage"""
    __tablename__ = "refresh_tokens"

    id: Mapped[int_pk] = mapped_column(primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False)  # Hashed token
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    revoked: Mapped[bool] = mapped_column(default=False)
    replaced_by_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Hashed
    created_at: Mapped[created_at]
    family_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # UUID format
    device_info: Mapped[Optional[str]] = mapped_column(String(200))
    previous_token_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("refresh_tokens.id"), 
        nullable=True
    )

    user: Mapped["UserModel"] = relationship(back_populates="refresh_tokens")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)