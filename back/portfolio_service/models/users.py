from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.portfolio_service.database import Base
from back.portfolio_service.schemas.users import SUser


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_user_id: Mapped[int]
    username: Mapped[str]

    portfolio: Mapped["Portfolio"] = relationship(back_populates="user")

    def read_model(self) -> SUser:
        return SUser(
            id=self.id,
            external_user_id=self.external_user_id,
            username=self.username
        )
