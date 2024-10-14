from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from back.portfolio_service.database import Base
from back.portfolio_service.schemas.assets import SAsset, AssetType


class Assets(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    symbol: Mapped[str]
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType))

    portfolio_assets: Mapped[list["PortfolioAssets"]] = relationship(back_populates="asset")
    transactions: Mapped[list["Transactions"]] = relationship(back_populates="asset")

    def read_model(self) -> SAsset:
        return SAsset(
            id=self.id,
            name=self.name,
            symbol=self.symbol,
            asset_type=self.asset_type
        )
