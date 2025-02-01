from pydantic import BaseModel

from back.portfolio_service.schemas.assets import AssetType


class SPortfolioAsset(BaseModel):
    id: int
    asset_id: int
    name: str
    symbol: str
    asset_type: AssetType
    quantity: float

    class Config:
        from_attributes = True


class SPortfolioAssetMarketData(SPortfolioAsset):
    current_price: float
    usd_24h_change: float
    last_updated: str


class SPortfolioAssetCreate(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: float


class SPortfolioAssetUpdate(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: float
