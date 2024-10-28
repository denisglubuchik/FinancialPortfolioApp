from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.portfolio_service.database import Base
from back.portfolio_service.schemas.users import SUser


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    username: Mapped[str]

    portfolio: Mapped["Portfolio"] = relationship(back_populates="user",
                                                  cascade="all, delete-orphan",
                                                  passive_deletes=True)

    def read_model(self) -> SUser:
        return SUser(
            id=self.id,
            username=self.username
        )
