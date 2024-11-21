from enum import Enum

from pydantic import BaseModel
from datetime import datetime


class TransactionType(str, Enum):
    buy = "buy"
    sell = "sell"


class STransaction(BaseModel):
    id: int
    portfolio_id: int
    asset_id: int
    transaction_type: TransactionType
    quantity: float
    price: int
    total_price: int
    transaction_date: datetime

    class Config:
        from_attributes = True


class STransactionCreate(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: float
    transaction_type: TransactionType
    price: int
    transaction_date: datetime
