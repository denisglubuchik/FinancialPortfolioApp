import json
import logging
import httpx

from bot.core.config import settings

logger = logging.getLogger("__name__")


async def add_new_user(tg_id: int, username: str):
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "tg_id": tg_id,
                "username": username
            }
            response = await client.post(f"{settings.gateway_url}/tg/login", params=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"{e.response.status_code} {e.response.json().get('detail')}")
    except json.decoder.JSONDecodeError:
        logger.error(f"500 Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"{str(e)}")


async def get_user_by_tg(tg_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.gateway_url}/tg/users/{tg_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"{e.response.status_code} {e.response.json().get('detail')}")
    except json.decoder.JSONDecodeError:
        logger.error(f"500 Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"{str(e)}")


async def change_email(tg_id: int, new_email: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{settings.gateway_url}/tg/users/{tg_id}/email?new_email={new_email}")
            response.raise_for_status()
            return "Email изменен"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return "Вы ввели тот же email"
        logger.error(f"{e.response.status_code} {e.response.json().get('detail')}")
    except json.decoder.JSONDecodeError:
        logger.error(f"500 Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"{str(e)}")
