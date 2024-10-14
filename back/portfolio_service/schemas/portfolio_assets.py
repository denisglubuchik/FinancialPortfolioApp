from pydantic import BaseModel


class SPortfolioAsset(BaseModel):
    id: int
    portfolio_id: int
    asset_id: int
    quantity: float

    class Config:
        from_attributes = True


class SPortfolioAssetCreate(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: float


class SPortfolioAssetUpdate(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: float
