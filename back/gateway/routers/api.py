import json
import logging

import httpx
from fastapi import Depends, Form, HTTPException, APIRouter
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from back.gateway.auth.dependencies import validate_user_creds, get_current_auth_user, get_current_auth_user_for_refresh
from back.gateway.auth.helpers import create_access_token, create_refresh_token
from back.gateway.schemas import SUserCreate, STransactionCreate, TokenInfo, SUser, SUserUpdate, datetime_encoder

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/api",
    tags=["api"],
    dependencies=[Depends(http_bearer)]
)

services = {
    "portfolio": "http://portfolio_app:8000",
    "user": "http://user_app:8001",
}


@router.post("/register")
async def register(user: SUserCreate):
    logger.info(f"User registration request: username={user.username}, email={user.email}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{services['user']}/users/register", json=user.model_dump())
            response.raise_for_status()
            result = response.json()
            logger.info(f"User registration successful: user_id={result.get('id')}, username={user.username}")
            return result
    except httpx.HTTPStatusError as e:
        logger.error(f"User registration failed for username {user.username}: HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response during registration for username {user.username}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error during registration for username {user.username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(user: SUser = Depends(validate_user_creds)):
    logger.info(f"User login successful: user_id={user.id}, username={user.username}")
    
    try:
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        logger.debug(f"Tokens created for user_id: {user.id}")
        return TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except Exception as e:
        logger.error(f"Token creation failed for user_id {user.id}: {e}")
        raise HTTPException(status_code=500, detail="Token creation failed")


class UpdatedUserAndToken(BaseModel):
    updated_user: SUser
    token: TokenInfo


@router.put(
    "/users/update",
    response_model=SUser | UpdatedUserAndToken,
    response_model_exclude_none=True
)
async def update_user(updated_user: SUserUpdate, current_user: SUser = Depends(get_current_auth_user)):
    logger.info(f"User update request: user_id={current_user.id}")
    
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
            logger.info(f"Username changed for user_id {current_user.id}: {current_user.username} -> {updated_user_from_user_service.username}")
            access_token = create_access_token(updated_user_from_user_service)
            return UpdatedUserAndToken(updated_user=updated_user_from_user_service,
                                       token=TokenInfo(access_token=access_token))
        
        logger.info(f"User updated successfully: user_id={current_user.id}")
        return updated_user_from_user_service

    except httpx.HTTPStatusError as e:
        logger.error(f"User update failed for user_id {current_user.id}: HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response during update for user_id {current_user.id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error during update for user_id {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/password")
async def update_user_password(current_password: str, new_password: str, user: SUser = Depends(get_current_auth_user)):
    logger.info(f"Password change request for user_id: {user.id}")
    
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
            logger.info(f"Password changed successfully for user_id: {user.id}")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Password change failed for user_id {user.id}: HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response during password change for user_id {user.id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error during password change for user_id {user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/me")
async def get_me(user: SUser = Depends(get_current_auth_user)) -> SUser:
    logger.debug(f"User profile request: user_id={user.id}")
    return user


@router.post(
    "/users/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def auth_refresh_jwt(
        user: SUser = Depends(get_current_auth_user_for_refresh),
):
    logger.debug(f"Token refresh request for user_id: {user.id}")
    
    try:
        access_token = create_access_token(user)
        logger.debug(f"Token refreshed successfully for user_id: {user.id}")
        return TokenInfo(
            access_token=access_token,
        )
    except Exception as e:
        logger.error(f"Token refresh failed for user_id {user.id}: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.delete("/users")
async def delete_user(user: SUser = Depends(get_current_auth_user)):
    logger.info(f"User deletion request: user_id={user.id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{services['user']}/users/", params={"user_id": user.id})
            response.raise_for_status()
            logger.info(f"User deleted successfully: user_id={user.id}")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"User deletion failed for user_id {user.id}: HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response during deletion for user_id {user.id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error during deletion for user_id {user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/verification_code")
async def get_verification_code(user: SUser = Depends(get_current_auth_user)):
    logger.info(f"Verification code request for user_id: {user.id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['user']}/users/verification_code", params={"user_id": user.id})
            response.raise_for_status()
            logger.info(f"Verification code sent for user_id: {user.id}")
            return response.json()
    except Exception as e:
        logger.error(f"Verification code request failed for user_id {user.id}: {e}")
        raise


@router.post("/users/verification_code")
async def post_verification_code(code: str = Form(), user: SUser = Depends(get_current_auth_user)):
    logger.info(f"Email verification attempt for user_id: {user.id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{services['user']}/users/verification_code",
                                         json={"user_id": user.id, "code": code})
            response.raise_for_status()
            logger.info(f"Email verified successfully for user_id: {user.id}")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.warning(f"Email verification failed for user_id {user.id}: HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response during verification for user_id {user.id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error during verification for user_id {user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/by_user_id/{user_id}")
async def get_portfolio_by_user_id(user_id: int):
    logger.debug(f"Portfolio request by user_id: {user_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/portfolio/by_user_id/{user_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.warning(f"Portfolio not found for user_id {user_id}: HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response for portfolio user_id {user_id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error fetching portfolio for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/{portfolio_id}")
async def get_portfolio(portfolio_id: int):
    logger.debug(f"Portfolio request by portfolio_id: {portfolio_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{services['portfolio']}/portfolio/{portfolio_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.warning(f"Portfolio not found: portfolio_id={portfolio_id}, HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response for portfolio_id {portfolio_id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error fetching portfolio_id {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio/{portfolio_id}/transactions")
async def post_transaction(transaction: STransactionCreate, portfolio_id: int, user: SUser = Depends(get_current_auth_user)):
    logger.info(f"Transaction creation request: portfolio_id={portfolio_id}, user_id={user.id}, type={transaction.transaction_type}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{services['portfolio']}/transactions/?user_id={user.id}&portfolio_id={portfolio_id}",
                json=transaction.model_dump()
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Transaction created successfully: transaction_id={result}, portfolio_id={portfolio_id}")
            return result
    except httpx.HTTPStatusError as e:
        logger.error(f"Transaction creation failed for portfolio_id {portfolio_id}: HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response during transaction creation for portfolio_id {portfolio_id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error during transaction creation for portfolio_id {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/{portfolio_id}/transactions")
async def get_transactions(portfolio_id: int, user: SUser = Depends(get_current_auth_user)):
    logger.debug(f"Fetching transactions for portfolio_id: {portfolio_id}, user_id: {user.id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{services['portfolio']}/transactions/?user_id={user.id}&portfolio_id={portfolio_id}",
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Found {len(result)} transactions for portfolio_id: {portfolio_id}")
            return result
    except httpx.HTTPStatusError as e:
        logger.warning(f"Failed to fetch transactions for portfolio_id {portfolio_id}: HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response fetching transactions for portfolio_id {portfolio_id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error fetching transactions for portfolio_id {portfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/{portfolio_id}/transactions/{transaction_id}")  # юзер не может получить чужие транзакции
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


@router.delete("/portfolio/{portfolio_id}/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int, user: SUser = Depends(get_current_auth_user)):
    logger.info(f"Deleting transaction: transaction_id={transaction_id}, user_id={user.id}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{services['portfolio']}/transactions/{transaction_id}?user_id={user.id}")
            response.raise_for_status()
            logger.info(f"Transaction deleted successfully: transaction_id={transaction_id}")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Transaction deletion failed for transaction_id {transaction_id}: HTTP {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except json.decoder.JSONDecodeError:
        logger.error(f"Invalid JSON response during transaction deletion for transaction_id {transaction_id}: {response.text}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON response, {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error during transaction deletion for transaction_id {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/{portfolio_id}/assets")
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
