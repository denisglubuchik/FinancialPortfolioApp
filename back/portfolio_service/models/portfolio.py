from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.portfolio_service.database import Base
from back.portfolio_service.schemas.portfolio import SPortfolio


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_invested: Mapped[float] = mapped_column(default=0)
    current_value: Mapped[float] = mapped_column(default=0)

    user: Mapped["Users"] = relationship(back_populates="portfolio")
    portfolio_assets: Mapped[list["PortfolioAssets"]] = relationship(back_populates="portfolio")
    transactions: Mapped[list["Transactions"]] = relationship(back_populates="portfolio")

    def read_model(self) -> SPortfolio:
        return SPortfolio(
            id=self.id,
            user_id=self.user_id,
            total_invested=self.total_invested,
            current_value=self.current_value
        )
