import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from back.logging import setup_logging_base_config
from back.config import MarketDataSettings, RedisSettings
from back.market_data_service.market_data_fetcher import MarketDataFetcher
from back.market_data_service.redis import RedisClient


setup_logging_base_config()
logger = logging.getLogger(__name__)

market_data_settings = MarketDataSettings()
redis_settings = RedisSettings()

CRYPTO_ASSETS = [
    "bitcoin", "ethereum", "solana", "tether", "usd-coin", "ripple", "binancecoin",
    "the-open-network", "dogecoin", "shiba-inu", "grass", "official-trump", "optimism",
    "ethereum-classic", "berachain-bera", "cardano", "tron", "chainlink", "avalanche-2",
    "leo-token", "stellar", "sui", "hedera-hashgraph", "litecoin", "polkadot", "bitcoin-cash",
    "bitget-token", "pi-network", "hyperliquid", "whitebit", "monero", "layerzero", "uniswap",
    "near", "aptos", "pepe", "arbitrum", "dai", "okb", "pudgy-penguins", "internet-computer",
    "tokenize-xchange", "gatechain-token", "ondo-finance", "mantle", "aave", "crypto-com-chain",
    "ethena", "bittensor", "vechain", "cosmos", "celestia", "render-token", "polygon-ecosystem-token",
    "kaspa", "filecoin", "sonic-3", "algorand", "fasttoken", "jupiter", "story-2", "fetch-ai",
    "kucoin-shares", "movement", "maker", "nexo", "immutable-x", "worldcoin", "bonk", "sei-network",
    "theta-token", "eos", "gala", "dydx", "the-sandbox", "jito-governance-token", "iota",
    "pancakeswap-token", "zcash", "honey-3", "walrus-2", "dogwifcoin", "starknet", "thorchain",
    "apecoin", "aerodrome-finance", "matic-network", "trust-wallet-token", "morpho", "plume"
]




async def update_market_data(market_data_fetcher: MarketDataFetcher, redis_client: RedisClient):
    logger.info("Starting market data update")
    try:
        market_data_crypto = await market_data_fetcher.fetch_market_data_crypto(CRYPTO_ASSETS)
        if market_data_crypto:
            processed_count = 0
            for asset, data in market_data_crypto.items():
                current_price = data.get("usd")
                usd_24h_change = data.get("usd_24h_change")
                last_updated_unix = data.get("last_updated_at")

                if current_price is not None and usd_24h_change is not None and last_updated_unix is not None:
                    await redis_client.save_market_data_crypto(asset, current_price, usd_24h_change, last_updated_unix)
                    processed_count += 1
                else:
                    logger.warning(f"Invalid data for asset {asset}: {data}")
            
            logger.info(f"Market data update completed. Processed {processed_count} assets.")
        else:
            logger.warning("No market data received from fetcher")
    except Exception as e:
        logger.error(f"Error during market data update: {e}")


async def start_scheduler(market_fetcher: MarketDataFetcher, redis_client: RedisClient):
    logger.info("Starting market data scheduler")
    scheduler = AsyncIOScheduler()

    scheduler.add_job(update_market_data, 'interval', minutes=3, args=[market_fetcher, redis_client])
    scheduler.start()
    logger.info("Market data scheduler started with 3-minute intervals")

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Shutting down market data scheduler")
        scheduler.shutdown()
        logger.info("Market data scheduler shutdown complete")

async def main():
    logger.info("Starting market data service")
    
    market_data_fetcher = MarketDataFetcher(market_data_settings.COINGECKO_URL, market_data_settings.COINGECKO_API_KEY)
    redis_client = RedisClient(redis_settings.REDIS_HOST, redis_settings.REDIS_PORT, redis_settings.REDIS_DB)

    try:
        await redis_client.connect()
        logger.info("Redis client connected in market data service")
        await start_scheduler(market_data_fetcher, redis_client)
    except Exception as e:
        logger.error(f"Error in market data service main: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
