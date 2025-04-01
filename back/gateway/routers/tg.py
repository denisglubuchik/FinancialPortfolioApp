import json

import httpx
from fastapi import APIRouter, HTTPException, Request

from back.gateway.schemas import STransactionCreate

services = {
    "portfolio": "http://portfolio_app:8000",
    "user": "http://user_app:8001",
}


router = APIRouter(
    prefix="/tg",
    tags=["tg"],
)


@router.post("/login")
async def telegram_login(tg_id: int, username: str):
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "tg_id": tg_id,
                "username": username
            }
            response = await client.post(f"{services['user']}/users/telegram_login", params=payload)

            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{tg_id}")
async def get_user_by_tg(tg_id: int):
    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(f"{services['user']}/users/user/by_tg/{tg_id}")
            user_response.raise_for_status()
            user_data = user_response.json()
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")
            return user_data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {user_response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{tg_id}/email")
async def update_user(tg_id: int, new_email: str):
    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.put(f"{services['user']}/users/email?tg_id={tg_id}&new_email={new_email}")
            user_response.raise_for_status()
            user_data = user_response.json()
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")
            return user_data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {user_response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/by_tg/{tg_id}")
async def get_portfolio_by_tg(tg_id: int):
    # Получаем user_id по tg_id
    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(f"{services['user']}/users/user/by_tg/{tg_id}")
            user_response.raise_for_status()
            user_data = user_response.json()
            user_id = user_data.get("id")
            if not user_id:
                raise HTTPException(status_code=404, detail="User not found")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {user_response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Запрашиваем портфель по user_id
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/portfolio/by_user_id/{user_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/{portfolio_id}/assets")
async def get_assets(portfolio_id: int, user_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/portfolio_assets/{portfolio_id}?user_id={user_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets/")
async def get_assets():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/assets/")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio/{portfolio_id}/transactions")
async def post_transaction(transaction: STransactionCreate, portfolio_id: int, user_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{services['portfolio']}/transactions/?user_id={user_id}&portfolio_id={portfolio_id}",
                json=transaction.model_dump()
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
