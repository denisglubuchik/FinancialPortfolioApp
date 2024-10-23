from datetime import datetime

from pydantic import BaseModel


class SVerificationToken(BaseModel):
    id: int
    user_id: int
    verification_token: str
    is_used: bool
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class SVerificationTokenCreate(BaseModel):
    user_id: int
    created_at: datetime
    expires_at: datetime
