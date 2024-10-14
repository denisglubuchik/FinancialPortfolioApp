from pydantic import BaseModel


class SCreateUser(BaseModel):
    username: str
    password: str
    email: str


class SUser(BaseModel):
    id: int
    username: str
    email: str
    registered_at: str

    class Config:
        from_attributes = True


class SUpdateUser(BaseModel):
    username: str
    email: str
    password: str
