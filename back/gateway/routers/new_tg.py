from fastapi import APIRouter, HTTPException, Request, Depends

from back.gateway.schemas import STransactionCreate
from back.gateway.service import ServiceClient

# Конфигурация сервисов
SERVICES = {
    "portfolio": "http://portfolio_app:8000",
    "user": "http://user_app:8001",
}

# Маршрутизатор
router = APIRouter(
    prefix="/tg",
    tags=["tg"],
)


async def get_service_client() -> ServiceClient:
    """Dependency для внедрения клиента сервисов"""
    client = ServiceClient(SERVICES)
    try:
        yield client
    finally:
        await client.close()

@router.post("/login")
async def telegram_login(
        tg_id: int,
        username: str,
        client: ServiceClient = Depends(get_service_client)
):
    """Авторизация пользователя через Telegram"""
    return await client.post(
        service="user",
        endpoint="/users/telegram_login",
        params={"tg_id": tg_id, "username": username}
    )


@router.get("/users/{tg_id}")
async def get_user_by_tg(
        tg_id: int,
        client: ServiceClient = Depends(get_service_client)
):
    """Получение информации о пользователе по Telegram ID"""
    user_data = await client.get(
        service="user",
        endpoint=f"/users/user/by_tg/{tg_id}"
    )

    if not user_data:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user_data


@router.put("/users/{tg_id}/email")
async def update_user(
        tg_id: int,
        new_email: str,
        client: ServiceClient = Depends(get_service_client)
):
    """Обновление email пользователя"""
    user_data = await client.put(
        service="user",
        endpoint="/users/email",
        params={"tg_id": tg_id, "new_email": new_email}
    )

    if not user_data:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user_data


@router.get("/portfolio/{tg_id}")
async def get_portfolio_by_tg(
        tg_id: int,
        client: ServiceClient = Depends(get_service_client)
):
    """Получение портфеля пользователя по Telegram ID"""
    # Получаем user_id по tg_id
    user_data = await client.get(
        service="user",
        endpoint=f"/users/user/by_tg/{tg_id}"
    )

    user_id = user_data.get("id")
    if not user_id:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Запрашиваем портфель по user_id
    return await client.get(
        service="portfolio",
        endpoint=f"/portfolio/by_user_id/{user_id}",
        headers={"X-User-ID": str(user_id)}
    )


@router.get("/portfolio/{portfolio_id}/assets")
async def get_assets(
        portfolio_id: int,
        user_id: int,
        client: ServiceClient = Depends(get_service_client)
):
    """Получение активов портфеля"""
    return await client.get(
        service="portfolio",
        endpoint=f"/portfolio_assets/{portfolio_id}",
        params={"user_id": user_id},
        headers={"X-User-ID": str(user_id)}
    )


@router.get("/assets/")
async def get_assets(client: ServiceClient = Depends(get_service_client)):
    """Получение списка всех активов"""
    return await client.get(
        service="portfolio",
        endpoint="/assets/"
    )


@router.post("/portfolio/{portfolio_id}/transactions")
async def post_transaction(
        transaction: STransactionCreate,
        portfolio_id: int,
        user_id: int,
        client: ServiceClient = Depends(get_service_client)
):
    """Создание новой транзакции"""
    return await client.post(
        service="portfolio",
        endpoint="/transactions/",
        params={"user_id": user_id, "portfolio_id": portfolio_id},
        headers={"X-User-ID": str(user_id)},
        json_data=transaction.model_dump()
    )
