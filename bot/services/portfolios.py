import json
import logging
from datetime import datetime

import httpx

from bot.core.config import settings

logger = logging.getLogger("__name__")


async def get_portfolio(tg_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.gateway_url}/tg/portfolio/{tg_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"{e.response.status_code} {e.response.json().get('detail')}")
    except json.decoder.JSONDecodeError:
        logger.error(f"500 Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"{str(e)}")


async def get_portfolio_assets(back_user_id: int, back_portfolio_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.gateway_url}/tg/portfolio/{back_portfolio_id}/assets?user_id={back_user_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"{e.response.status_code} {e.response.json().get('detail')}")
    except json.decoder.JSONDecodeError:
        logger.error(f"500 Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"{str(e)}")


async def get_assets():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.gateway_url}/tg/assets/")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"{e.response.status_code} {e.response.json().get('detail')}")
    except json.decoder.JSONDecodeError:
        logger.error(f"500 Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"{str(e)}")


async def add_transaction(
    back_user_id: int, back_portfolio_id: int,
    asset_id: int, transaction_type: str,
    quantity: float, price: int
):
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "asset_id": asset_id,
                "quantity": quantity,
                "transaction_type": transaction_type,
                "price": price,
                "transaction_date": datetime.now().isoformat()
            }
            response = await client.post(f"{settings.gateway_url}/tg/portfolio/{back_portfolio_id}/transactions?user_id={back_user_id}",
                                         json=payload)
            response.raise_for_status()
            return "Добавлена новая транзакция"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            return "У вас нет нужного количества активов для продажи"
        logger.error(f"{e.response.status_code} {e.response.json().get('detail')}")
    except json.decoder.JSONDecodeError:
        logger.error(f"500 Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"{str(e)}")
