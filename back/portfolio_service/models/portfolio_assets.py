from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.portfolio_service.database import Base
from back.portfolio_service.schemas.portfolio_assets import SPortfolioAsset


class PortfolioAssets(Base):
    __tablename__ = "portfolio_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id", ondelete="CASCADE"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    quantity: Mapped[float]

    portfolio: Mapped["Portfolio"] = relationship(back_populates="portfolio_assets")
    asset: Mapped["Assets"] = relationship(back_populates="portfolio_assets")

    def read_model(self) -> SPortfolioAsset:
        return SPortfolioAsset(
            id=self.id,
            portfolio_id=self.portfolio_id,
            asset_id=self.asset_id,
            quantity=self.quantity
        )
