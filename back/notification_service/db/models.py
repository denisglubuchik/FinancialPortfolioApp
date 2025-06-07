from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, func, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.notification_service.db.database import Base


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    email: Mapped[str] = mapped_column(String)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)

    notifications: Mapped[list["Notifications"]] = relationship("Notifications",
                                                                back_populates="user",
                                                                cascade="all, delete-orphan",
                                                                passive_deletes=True)


class Notifications(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    notification_type: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    delivery_status: Mapped[str] = mapped_column(String, default=DeliveryStatus.PENDING)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["Users"] = relationship(back_populates="notifications")