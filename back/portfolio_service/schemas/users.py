from pydantic import BaseModel


class SUser(BaseModel):
    id: int
    external_user_id: int
    username: str

    class Config:
        from_attributes = True
