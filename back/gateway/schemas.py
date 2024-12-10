from datetime import datetime
from enum import Enum

from pydantic import BaseModel, field_validator, ConfigDict


class SUser(BaseModel):
    id: int
    username: str
    hashed_password: str
    is_verified: bool
    email: str
    registered_at: datetime

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


def datetime_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()


class SUserCreate(BaseModel):
    username: str
    hashed_password: str
    email: str


class SUserUpdate(BaseModel):
    username: str = "string"
    email: str = "string"


class TransactionType(str, Enum):
    buy = "buy"
    sell = "sell"


class STransactionCreate(BaseModel):
    asset_id: int
    quantity: float
    transaction_type: TransactionType
    price: int
    transaction_date: datetime

    @field_validator("transaction_date")
    def transaction_date(cls, v):
        return v.isoformat()


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
