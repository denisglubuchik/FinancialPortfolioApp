import uuid
from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from back.config import UserSettings

user_settings = UserSettings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encode_jwt(
    payload: dict,
    secret_key: str = user_settings.SECRET_KEY,
    algorithm: str = user_settings.ALGORITHM,
    expire_minutes: int = 60,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(
        to_encode,
        secret_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    secret_key: str = user_settings.SECRET_KEY,
    algorithm: str = user_settings.ALGORITHM,
) -> dict:
    decoded = jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def validate_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
