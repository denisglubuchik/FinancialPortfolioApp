from pydantic_settings import BaseSettings


class UserSettings(BaseSettings):
    pass


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
