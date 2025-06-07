import json
import logging
from typing import Dict, Optional, Any, Union

import httpx


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceClient:
    """Класс для взаимодействия с микросервисами"""

    def __init__(self, services: Dict[str, str]):
        self.services = services
        self.client = httpx.AsyncClient(timeout=1)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.client.aclose()

    async def request(
            self,
            method: str,
            service: str,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            content: Optional[Union[str, bytes]] = None,
            data: Optional[Dict[str, Any]] = None,
            files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Выполняет запрос к микросервису и обрабатывает ошибки

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE, etc.)
            service: Имя сервиса из конфигурации
            endpoint: Путь эндпоинта
            params: URL параметры запроса (query params)
            json_data: JSON данные для тела запроса
            headers: HTTP заголовки
            cookies: HTTP cookies
            content: Контент (строка или байты) для тела запроса
            data: Данные формы для тела запроса
            files: Файлы для отправки

        Returns:
            Dict[str, Any]: Ответ сервиса в формате JSON
        """
        if service not in self.services:
            raise ValueError(f"Неизвестный сервис: {service}")

        url = f"{self.services[service]}{endpoint}"

        # Формируем базовые заголовки, которые можно переопределить
        default_headers = {"Accept": "application/json"}
        if headers:
            default_headers.update(headers)

        try:
            logger.info(f"Отправка {method} запроса к {url}")
            logger.debug(f"Параметры: params={params}, headers={default_headers}, json={json_data}, data={data}")

            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=default_headers,
                cookies=cookies,
                content=content,
                data=data,
                files=files
            )
            response.raise_for_status()

            # Проверяем, что ответ содержит JSON
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                # Если не JSON, возвращаем текст и заголовки
                return {
                    "content": response.text,
                    "headers": dict(response.headers),
                    "status_code": response.status_code
                }


        except httpx.HTTPStatusError as e:
            # Просто пробрасываем исключение дальше для обработки на уровне вызывающих функций
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {str(e)} - {response.text}")
            raise httpx.HTTPError(f"Недопустимый JSON ответ: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {str(e)}")
            raise httpx.HTTPError(f"Ошибка запроса: {str(e)}")

    # Удобные методы для разных типов запросов
    async def get(self, service: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        return await self.request("GET", service, endpoint, **kwargs)

    async def post(self, service: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        return await self.request("POST", service, endpoint, **kwargs)

    async def put(self, service: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        return await self.request("PUT", service, endpoint, **kwargs)

    async def delete(self, service: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        return await self.request("DELETE", service, endpoint, **kwargs)

    async def patch(self, service: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        return await self.request("PATCH", service, endpoint, **kwargs)
