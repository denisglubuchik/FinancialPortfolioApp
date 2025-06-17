import httpx
import logging

logger = logging.getLogger(__name__)


class MarketDataFetcher:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    async def fetch_market_data_crypto(self, crypto_assets):
        try:
            async with httpx.AsyncClient() as client:
                headers = {"accept": "application/json", "x-cg-demo-api-key": self.api_key}
                params = {"ids": ','.join(crypto_assets), "vs_currencies": "usd",
                          "include_24hr_change": "true", "include_last_updated_at": "true"}
                response = await client.get(self.api_url, headers=headers, params=params)
                response.raise_for_status()

            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error in market data fetch: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error in market data fetch: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error in market data fetch: {e}")
