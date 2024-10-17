from datetime import datetime

from sqlalchemy import DateTime, func, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.user_service.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    verification_tokens: Mapped[list['VerificationTokens']] = relationship(back_populates="user",
                                                                           cascade="all, delete-orphan",
                                                                           passive_deletes=True)
    refresh_tokens: Mapped[list['RefreshTokens']] = relationship(back_populates="user",
                                                                 cascade="all, delete-orphan",
                                                                 passive_deletes=True)
