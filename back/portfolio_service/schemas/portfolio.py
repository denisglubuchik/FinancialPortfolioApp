from pydantic import BaseModel


class SPortfolio(BaseModel):
    id: int
    user_id: int
    total_invested: float
    current_value: float

    class Config:
        from_attributes = True


class SPortfolioCreate(BaseModel):
    user_id: int


class SPortfolioUpdate(BaseModel):
    id: int
    total_invested: float
    current_value: float
