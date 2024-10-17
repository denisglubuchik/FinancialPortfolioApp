from pydantic_settings import BaseSettings


class UserSettings(BaseSettings):
    DB_USERS_HOST: str = "localhost"
    DB_USERS_PORT: int = 5433
    DB_USERS_NAME: str = "users_app"
    DB_USERS_USER: str = "sqluser"
    DB_USERS_PASSWORD: str = "sqlpass"


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
