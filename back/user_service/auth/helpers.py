from datetime import timedelta

from pydantic import BaseModel

from back.user_service.auth import utils as auth_utils
from back.user_service.schemas.users import SUser


ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class Payload(BaseModel):
    sub: str
    user_id: int
    username: str
    email: str


class JWTPayload(Payload):
    token_type: str


def create_jwt(
    token_type: str,
    token_data: Payload,
    expire_minutes: int = 60,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = JWTPayload(
        token_type=token_type,
        **token_data.model_dump(),
    )
    return auth_utils.encode_jwt(
        payload=jwt_payload.model_dump(),
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def create_access_token(user: SUser) -> str:
    jwt_payload = Payload(
        sub=user.username,
        user_id=user.id,
        username=user.username,
        email=user.email,
    )
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=60,
    )


def create_refresh_token(user: SUser) -> str:
    jwt_payload = Payload(
        sub=user.username,
        user_id=user.id,
        username=user.username,
        email=user.email,
    )
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=7),
    )