from pydantic_settings import BaseSettings


class UserSettings(BaseSettings):
    DB_USERS_HOST: str = "192.168.0.101"
    DB_USERS_PORT: int = 5433
    DB_USERS_NAME: str = "user_app"
    DB_USERS_USER: str = "sqluser"
    DB_USERS_PASSWORD: str = "sqlpass"

    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"


class PortfolioSettings(BaseSettings):
    DB_PORTFOLIOS_HOST: str = "192.168.0.100"
    DB_PORTFOLIOS_PORT: int = 5432
    DB_PORTFOLIOS_NAME: str = "portfolio_app"
    DB_PORTFOLIOS_USER: str = "sqluser"
    DB_PORTFOLIOS_PASSWORD: str = "sqlpass"


class MarketDataSettings(BaseSettings):
    pass


class NotificationSettings(BaseSettings):
    pass


class AnalyticsSettings(BaseSettings):
    pass
