from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from back.user_service.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    hashed_password: Mapped[str]
    email: Mapped[str]
    registered_at = mapped_column(DateTime(timezone=True), default=func.now())