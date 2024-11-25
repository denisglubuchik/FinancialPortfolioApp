from datetime import datetime

from pydantic import BaseModel


class SUserCreate(BaseModel):
    username: str
    hashed_password: str
    email: str


class SUser(BaseModel):
    id: int
    username: str
    hashed_password: str
    is_verified: bool
    email: str
    registered_at: datetime

    class Config:
        from_attributes = True


class SUserUpdate(BaseModel):
    username: str = "string"
    email: str = "string"
