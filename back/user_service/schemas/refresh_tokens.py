from datetime import datetime

from pydantic import BaseModel


class SRefreshToken(BaseModel):
    id: int
    user_id: int
    refresh_token: str
    is_revoked: bool
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class SRefreshTokenCreate(BaseModel):
    user_id: int
    created_at: datetime
    expires_at: datetime
