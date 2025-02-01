from datetime import datetime

from aioredis import Redis


class RedisClient:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.redis = None

    async def connect(self):
        self.redis = await Redis(host=self.host, port=self.port, db=self.db)

    async def save_market_data_crypto(self, asset: str, current_price: float, usd_24h_change: float, last_updated_unix: float):
        key = f"market_data:{asset}"
        await self.redis.hset(key, mapping={
            "current_price": current_price,
            "usd_24h_change": usd_24h_change,
            "last_updated": datetime.fromtimestamp(last_updated_unix).isoformat()
        })

    async def close(self):
        if self.redis:
            await self.redis.close()
