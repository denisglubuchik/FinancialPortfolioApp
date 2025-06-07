import json
import logging
from datetime import datetime

import httpx

from bot.core.config import settings
from bot.services.base import ServiceClient

logger = logging.getLogger("__name__")


async def get_portfolio(tg_id: int):
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            return await client.get("gateway", f"/tg/portfolio/{tg_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"{e.response.status_code} {e.response.json().get('detail', '')}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"{str(e)}")
            return None
        except Exception as e:
            logger.error(f"{str(e)}")
            return None


async def get_portfolio_assets(back_user_id: int, back_portfolio_id: int):
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            params = {"user_id": back_user_id}
            return await client.get("gateway", f"/tg/portfolio/{back_portfolio_id}/assets", params=params)
        except httpx.HTTPStatusError as e:
            logger.error(f"{e.response.status_code} {e.response.json().get('detail', '')}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"{str(e)}")
            return None
        except Exception as e:
            logger.error(f"{str(e)}")
            return None


async def get_assets():
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            return await client.get("gateway", "/tg/assets/")
        except httpx.HTTPStatusError as e:
            logger.error(f"{e.response.status_code} {e.response.json().get('detail', '')}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"{str(e)}")
            return None
        except Exception as e:
            logger.error(f"{str(e)}")
            return None


async def add_transaction(
    back_user_id: int, back_portfolio_id: int,
    asset_id: int, transaction_type: str,
    quantity: float, price: int
):
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            payload = {
                "asset_id": asset_id,
                "quantity": quantity,
                "transaction_type": transaction_type,
                "price": price,
                "transaction_date": datetime.now().isoformat()
            }
            params = {"user_id": back_user_id}

            await client.post(
                "gateway",
                f"/tg/portfolio/{back_portfolio_id}/transactions",
                params=params,
                json_data=payload
            )
            return "Добавлена новая транзакция"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                return "У вас нет нужного количества активов для продажи"
            logger.error(f"{e.response.status_code} {e.response.json().get('detail', '')}")
            return f"Ошибка: {e.response.text}"
        except httpx.HTTPError as e:
            logger.error(f"{str(e)}")
            return f"Произошла ошибка: {str(e)}"
        except Exception as e:
            logger.error(f"{str(e)}")
            return f"Произошла ошибка: {str(e)}"
