from datetime import datetime

from sqlalchemy import DateTime, func, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.user_service.db.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    verification_tokens: Mapped[list["VerificationTokens"]] = relationship("VerificationTokens",
                                                                           back_populates="user",
                                                                           cascade="all, delete-orphan",
                                                                           passive_deletes=True)


class VerificationTokens(Base):
    __tablename__ = "verification_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    verification_token: Mapped[str] = mapped_column(String)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["Users"] = relationship(back_populates="verification_tokens")