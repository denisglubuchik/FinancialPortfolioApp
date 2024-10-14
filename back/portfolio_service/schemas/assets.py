from enum import Enum

from pydantic import BaseModel


class AssetType(Enum):
    crypto = "crypto"
    stock = "stock"
    fiat = "fiat"


class SAsset(BaseModel):
    id: int
    name: str
    symbol: str
    asset_type: AssetType

    class Config:
        from_attributes = True


class SAssetCreate(BaseModel):
    name: str
    symbol: str
    asset_type: AssetType
