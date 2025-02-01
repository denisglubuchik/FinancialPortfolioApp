from aioredis import Redis

from back.config import RedisSettings

redis_settings = RedisSettings()


class RedisClient:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.redis = None

    async def connect(self):
        self.redis = await Redis(host=self.host, port=self.port, db=self.db)

    async def get_asset(self, asset: str):
        key = f"market_data:{asset}"
        data = await self.redis.hgetall(key)
        return {k.decode(): v.decode() for k, v in data.items()}

    async def get_assets(self, assets: list[str]):
        res = {}
        for asset in assets:
            res[asset] = await self.get_asset(asset)
        return res

    async def close(self):
        if self.redis:
            await self.redis.close()


redis_client = RedisClient(redis_settings.REDIS_HOST, redis_settings.REDIS_PORT, redis_settings.REDIS_DB)