import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from back.config import MarketDataSettings, RedisSettings
from back.market_data_service.market_data_fetcher import MarketDataFetcher
from back.market_data_service.redis import RedisClient

market_data_settings = MarketDataSettings()
redis_settings = RedisSettings()

CRYPTO_ASSETS = ["bitcoin", "ethereum", "solana"]


async def update_market_data(market_data_fetcher: MarketDataFetcher, redis_client: RedisClient):
    market_data_crypto = await market_data_fetcher.fetch_market_data_crypto(CRYPTO_ASSETS)
    if market_data_crypto:
        for asset, data in market_data_crypto.items():
            current_price = data.get("usd")
            usd_24h_change = data.get("usd_24h_change")
            last_updated_unix = data.get("last_updated_at")

            if current_price is not None and usd_24h_change is not None and last_updated_unix is not None:
                await redis_client.save_market_data_crypto(asset, current_price, usd_24h_change, last_updated_unix)
            else:
                print(f"Invalid data for asset {asset}: {data}")


async def start_scheduler(market_fetcher: MarketDataFetcher, redis_client: RedisClient):
    scheduler = AsyncIOScheduler()

    scheduler.add_job(update_market_data, 'interval', minutes=1, args=[market_fetcher, redis_client])
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        scheduler.shutdown()

async def main():
    market_data_fetcher = MarketDataFetcher(market_data_settings.COINGECKO_URL, market_data_settings.COINGECKO_API_KEY)
    redis_client = RedisClient(redis_settings.REDIS_HOST, redis_settings.REDIS_PORT, redis_settings.REDIS_DB)

    await redis_client.connect()
    await start_scheduler(market_data_fetcher, redis_client)


if __name__ == "__main__":
    asyncio.run(main())
