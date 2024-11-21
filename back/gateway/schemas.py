from datetime import datetime
from enum import Enum

from pydantic import BaseModel, field_validator


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
    portfolio_id: int
    asset_id: int
    quantity: float
    transaction_type: TransactionType
    price: int
    transaction_date: datetime

    @field_validator("transaction_date")
    def transaction_date(cls, v):
        return v.isoformat()
