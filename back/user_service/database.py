from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from back.config import UserSettings


user_settings =UserSettings()

DB_URL = (f"postgresql+asyncpg://{user_settings.DB_USERS_USER}:"
          f"{user_settings.DB_USERS_PASSWORD}@"
          f"{user_settings.DB_USERS_HOST}:{user_settings.DB_USERS_HOST}/"
          f"{user_settings.DB_USERS_NAME}")


engine = create_async_engine(DB_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
