from datetime import datetime

from sqlalchemy import DateTime, func, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.notification_service.db.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    email: Mapped[str] = mapped_column(String)

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

    user: Mapped["Users"] = relationship(back_populates="notifications")