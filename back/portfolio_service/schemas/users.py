from pydantic import BaseModel


class SUser(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class SUserCreate(BaseModel):
    id: int
    username: str

