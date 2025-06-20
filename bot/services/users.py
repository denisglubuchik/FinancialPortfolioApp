import logging
import httpx

from bot.core.config import settings
from bot.services.base import ServiceClient

logger = logging.getLogger("__name__")


async def add_new_user(tg_id: int, username: str):
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            params = {
                "tg_id": tg_id,
                "username": username
            }
            return await client.post("gateway", "/tg/login", params=params)
        except httpx.HTTPStatusError as e:
            logger.error(f"{e.response.status_code} {e.response.json().get('detail', '')}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"{str(e)}")
            return None
        except Exception as e:
            logger.error(f"{str(e)}")
            return None


async def get_user_by_tg(tg_id: int):
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            return await client.get("gateway", f"/tg/users/{tg_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"{e.response.status_code} {e.response.json().get('detail', '')}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"{str(e)}")
            return None
        except Exception as e:
            logger.error(f"{str(e)}")
            return None


async def change_email(tg_id: int, new_email: str):
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            params = {"new_email": new_email}
            await client.put("gateway", f"/tg/users/{tg_id}/email", params=params)
            return "Email изменен"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                return "Вы ввели тот же email"
            logger.error(f"{e.response.status_code} {e.response.json().get('detail', '')}")
            return f"Ошибка: {e.response.text}"
        except httpx.HTTPError as e:
            logger.error(f"{str(e)}")
            return f"Произошла ошибка: {str(e)}"
        except Exception as e:
            logger.error(f"{str(e)}")
            return f"Произошла ошибка: {str(e)}"


async def request_verification_code(tg_id: int):
    """Запрос кода верификации email"""
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            response = await client.get("gateway", f"/tg/users/{tg_id}/verification_code")
            return "Код верификации отправлен на ваш email"
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get('detail', 'Неизвестная ошибка')
            logger.error(f"{e.response.status_code} {error_detail}")
            if e.response.status_code == 404:
                return "Пользователь не найден"
            return f"Ошибка: {error_detail}"
        except httpx.HTTPError as e:
            logger.error(f"{str(e)}")
            return f"Произошла ошибка: {str(e)}"
        except Exception as e:
            logger.error(f"{str(e)}")
            return f"Произошла ошибка: {str(e)}"


async def verify_email_code(tg_id: int, code: str):
    """Верификация email по коду"""
    async with ServiceClient({"gateway": settings.gateway_url}) as client:
        try:
            await client.post("gateway", f"/tg/users/{tg_id}/verification_code", params={"code": code})
            return "Email успешно верифицирован!"
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get('detail', 'Неизвестная ошибка')
            logger.error(f"{e.response.status_code} {error_detail}")
            if e.response.status_code == 404:
                return "Пользователь не найден или код не найден"
            elif e.response.status_code == 400:
                return "Неверный код верификации"
            return f"Ошибка: {error_detail}"
        except httpx.HTTPError as e:
            logger.error(f"{str(e)}")
            return f"Произошла ошибка: {str(e)}"
        except Exception as e:
            logger.error(f"{str(e)}")
            return f"Произошла ошибка: {str(e)}"
