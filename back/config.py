from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class RabbitMQSettings(EnvBaseSettings):
    RABBITMQ_MQ: str = "amqp://guest:guest@192.168.0.200:5672/"


class RedisSettings(EnvBaseSettings):
    REDIS_HOST: str = "192.168.0.201"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1


class UserSettings(EnvBaseSettings):
    DB_USERS_HOST: str = "192.168.0.101"
    DB_USERS_PORT: int = 5433
    DB_USERS_NAME: str = "user_app"
    DB_USERS_USER: str = "sqluser"
    DB_USERS_PASSWORD: str = "sqlpass"

    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"


class PortfolioSettings(EnvBaseSettings):
    DB_PORTFOLIOS_HOST: str = "192.168.0.100"
    DB_PORTFOLIOS_PORT: int = 5432
    DB_PORTFOLIOS_NAME: str = "portfolio_app"
    DB_PORTFOLIOS_USER: str = "sqluser"
    DB_PORTFOLIOS_PASSWORD: str = "sqlpass"


class MarketDataSettings(EnvBaseSettings):
    COINGECKO_API_KEY: str
    COINGECKO_URL: str


class NotificationSettings(EnvBaseSettings):
    DB_NOTIFICATIONS_HOST: str = "192.168.0.102"
    DB_NOTIFICATIONS_PORT: int = 5432
    DB_NOTIFICATIONS_NAME: str = "notification_app"
    DB_NOTIFICATIONS_USER: str = "sqluser"
    DB_NOTIFICATIONS_PASSWORD: str = "sqlpass"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "glubuchikdenis@gmail.com"
    SMTP_PASSWORD: str = "qwwh nuhu wglr gfyg"


class AnalyticsSettings(EnvBaseSettings):
    pass
