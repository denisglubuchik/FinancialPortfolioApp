from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from back.config import NotificationSettings


notification_settings = NotificationSettings()

DB_URL = (f"postgresql+asyncpg://{notification_settings.DB_NOTIFICATIONS_USER}:"
          f"{notification_settings.DB_NOTIFICATIONS_PASSWORD}@"
          f"{notification_settings.DB_NOTIFICATIONS_HOST}:{notification_settings.DB_NOTIFICATIONS_PORT}/"
          f"{notification_settings.DB_NOTIFICATIONS_NAME}")


engine = create_async_engine(DB_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
