from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# from back.portfolio_service.portfolio_main import portfolio_settings
from back.config import PortfolioSettings


portfolio_settings = PortfolioSettings()

DB_URL = (f"postgresql+asyncpg://{portfolio_settings.DB_PORTFOLIOS_USER}:"
          f"{portfolio_settings.DB_PORTFOLIOS_PASSWORD}@"
          f"{portfolio_settings.DB_PORTFOLIOS_HOST}:{portfolio_settings.DB_PORTFOLIOS_PORT}/"
          f"{portfolio_settings.DB_PORTFOLIOS_NAME}")


engine = create_async_engine(DB_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
