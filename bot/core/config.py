from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class RedisSettings(EnvBaseSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 2
    MARKET_REDIS_DB: int = 1

class BotSettings(EnvBaseSettings):
    BOT_TOKEN: str = "token"
    ADMIN_IDS: list[int] = [123]


class Settings(BotSettings, RedisSettings):
    GATEWAY: str = "api_gateway"
    GATEWAY_PORT: int = 7777

    @property
    def gateway_url(self) -> str:
        return f"http://{self.GATEWAY}:{self.GATEWAY_PORT}"

settings = Settings()
