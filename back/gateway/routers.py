import json

import httpx
from fastapi import FastAPI

from back.gateway.schemas import SUserCreate, STransactionCreate

api_gateway = FastAPI()

services = {
    "portfolio": "http://portfolio_app:8000",
    "user": "http://user_app:8001",
}


@api_gateway.post("/register")
async def register(user: SUserCreate):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{services['user']}/users/register/", json=user.model_dump())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": str(e), "status_code": e.response.status_code, "body": e.response.text,}
    except json.decoder.JSONDecodeError:
        return {"error": "Invalid JSON response", "body": response.text}
    except Exception as e:
        return {"error": str(e)}


@api_gateway.post("/login")
async def login():
    pass


@api_gateway.put("/users/update")
async def update_user():
    pass


@api_gateway.put("/users/password")
async def update_user_password():
    pass


@api_gateway.get("/users/me")
async def get_me():
    pass


@api_gateway.delete("/users")
async def delete_user():
    pass


@api_gateway.get("/users/verification_code")
async def get_verification_code():
    pass


@api_gateway.post("/users/verification_code")
async def post_verification_code():
    pass


@api_gateway.get("/portfolio/{portfolio_id}")
async def get_portfolio(portfolio_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{services['portfolio']}/portfolio/{portfolio_id}")
        return response.json()


@api_gateway.post("/portfolio/{portfolio_id}/transactions")
async def post_transaction(transaction: STransactionCreate):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{services['portfolio']}/transactions/", json=transaction.model_dump())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": str(e), "status_code": e.response.status_code, "body": e.response.text, }
    except json.decoder.JSONDecodeError:
        return {"error": "Invalid JSON response", "body": response.text}
    except Exception as e:
        return {"error": str(e)}


@api_gateway.get("/portfolio/{portfolio_id}/transactions")  # юзер может получить только свои транзакции
async def get_transactions(portfolio_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/transactions/", params={"portfolio_id": portfolio_id})
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": str(e), "status_code": e.response.status_code, "body": e.response.text,}
    except json.decoder.JSONDecodeError:
        return {"error": "Invalid JSON response", "body": response.text}
    except Exception as e:
        return {"error": str(e)}


@api_gateway.get("/portfolio/{portfolio_id}/transactions/{transaction_id}")  # юзер не может получить чужие транзакции
async def get_transaction(portfolio_id: int, transaction_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/transactions/{transaction_id}",
                                        params={"portfolio_id": portfolio_id})
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": str(e), "status_code": e.response.status_code, "body": e.response.text,}
    except json.decoder.JSONDecodeError:
        return {"error": "Invalid JSON response", "body": response.text}
    except Exception as e:
        return {"error": str(e)}


@api_gateway.get("/portfolio/{portfolio_id}/assets")
async def get_assets(portfolio_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{services['portfolio']}/portfolio_assets/{portfolio_id}")
        return response.json()

