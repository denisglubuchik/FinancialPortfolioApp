import json

import httpx
from fastapi import FastAPI, Depends, Form, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from back.gateway.auth.dependencies import validate_user_creds, get_current_auth_user, get_current_auth_user_for_refresh
from back.gateway.auth.helpers import create_access_token, create_refresh_token
from back.gateway.schemas import SUserCreate, STransactionCreate, TokenInfo, SUser, SUserUpdate, datetime_encoder

http_bearer = HTTPBearer(auto_error=False)

api_gateway = FastAPI(
    dependencies=[Depends(http_bearer)]
)

services = {
    "portfolio": "http://portfolio_app:8000",
    "user": "http://user_app:8001",
}


@api_gateway.post("/register")
async def register(user: SUserCreate):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{services['user']}/users/register", json=user.model_dump())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_gateway.post("/login")
async def login(user: SUser = Depends(validate_user_creds)):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


class UpdatedUserAndToken(BaseModel):
    updated_user: SUser
    token: TokenInfo


@api_gateway.put(
    "/users/update",
    response_model=SUser | UpdatedUserAndToken,
    response_model_exclude_none=True
)
async def update_user(updated_user: SUserUpdate, current_user: SUser = Depends(get_current_auth_user)):
    json_payload = json.dumps({
        "updated_user": updated_user.model_dump(),
        "current_user": current_user.model_dump(),
    }, default=datetime_encoder)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{services['user']}/users/",
                                        json=json.loads(json_payload))
            response.raise_for_status()
            updated_user_from_user_service = SUser(**response.json())

        # if user changes username, we need to update access token
        if current_user.username != updated_user_from_user_service.username:
            access_token = create_access_token(updated_user_from_user_service)
            return UpdatedUserAndToken(updated_user=updated_user_from_user_service,
                                       token=TokenInfo(access_token=access_token))
        return updated_user_from_user_service

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_gateway.put("/users/password")
async def update_user_password(current_password: str, new_password: str, user: SUser = Depends(get_current_auth_user)):
    json_payload = json.dumps({
        "current_password": current_password,
        "new_password": new_password,
        "user": user.model_dump(),
    }, default=datetime_encoder)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{services['user']}/users/password",
                                        json=json.loads(json_payload))
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_gateway.get("/users/me")
async def get_me(user: SUser = Depends(get_current_auth_user)) -> SUser:
    return user


@api_gateway.post(
    "/users/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def auth_refresh_jwt(
        user: SUser = Depends(get_current_auth_user_for_refresh),
):
    access_token = create_access_token(user)
    return TokenInfo(
        access_token=access_token,
    )


@api_gateway.delete("/users")
async def delete_user(user: SUser = Depends(get_current_auth_user)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{services['user']}/users/", params={"user_id": user.id})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_gateway.get("/users/verification_code")
async def get_verification_code(user: SUser = Depends(get_current_auth_user)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{services['user']}/users/verification_code", params={"user_id": user.id})
        return response.json()


@api_gateway.post("/users/verification_code")
async def post_verification_code(code: str = Form(), user: SUser = Depends(get_current_auth_user)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{services['user']}/users/verification_code",
                                         json={"user_id": user.id, "code": code})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_gateway.get("/portfolio/{portfolio_id}")
async def get_portfolio(portfolio_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/portfolio/{portfolio_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_gateway.post("/portfolio/{portfolio_id}/transactions")
async def post_transaction(transaction: STransactionCreate, portfolio_id: int, user: SUser = Depends(get_current_auth_user)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{services['portfolio']}/transactions/?user_id={user.id}&portfolio_id={portfolio_id}",
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


@api_gateway.get("/portfolio/{portfolio_id}/transactions")  # юзер может получить только свои транзакции
async def get_transactions(portfolio_id: int, user: SUser = Depends(get_current_auth_user)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{services['portfolio']}/transactions/?user_id={user.id}&portfolio_id={portfolio_id}",
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_gateway.get("/portfolio/{portfolio_id}/transactions/{transaction_id}")  # юзер не может получить чужие транзакции
async def get_transaction(transaction_id: int, user: SUser = Depends(get_current_auth_user)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/transactions/{transaction_id}?user_id={user.id}")
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_gateway.delete("/portfolio/{portfolio_id}/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int, user: SUser = Depends(get_current_auth_user)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{services['portfolio']}/transactions/{transaction_id}?user_id={user.id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_gateway.get("/portfolio/{portfolio_id}/assets")
async def get_assets(portfolio_id: int, user: SUser = Depends(get_current_auth_user)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/portfolio_assets/{portfolio_id}?user_id={user.id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
