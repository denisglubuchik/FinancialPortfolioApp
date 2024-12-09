import json

import httpx
from fastapi import Form, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from back.gateway.auth.exceptions import InvalidTokenException, InvalidTokenTypeException
from back.gateway.auth.helpers import JWTPayload, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from back.gateway.schemas import SUser
from back.gateway.auth import utils as auth_utils


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login",
)


async def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> JWTPayload:
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise InvalidTokenException(e)
    return JWTPayload(**payload)


async def validate_token_type(
    payload: JWTPayload,
    token_type: str,
) -> bool:
    current_token_type = payload.token_type
    if current_token_type == token_type:
        return True
    raise InvalidTokenTypeException(current_token_type, token_type)


async def get_user_by_token_sub(payload: JWTPayload) -> SUser:
    from back.gateway.routers import services

    username: str | None = payload.sub
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{services['user']}/users/user", params={"username": username})
        return SUser.model_validate(response.json())


class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(
        self,
        payload: JWTPayload = Depends(get_current_token_payload),
    ):
        await validate_token_type(payload, self.token_type)
        return await get_user_by_token_sub(payload)


get_current_auth_user = UserGetterFromToken(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = UserGetterFromToken(REFRESH_TOKEN_TYPE)


async def validate_user_creds(
        username: str = Form(),
        password: str = Form(),
) -> SUser:
    from back.gateway.routers import services
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{services['user']}/users/verify_credentials",
                                         json={
                                             "username": username,
                                             "password": password
                                         })
            response.raise_for_status()
            return SUser.model_validate(response.json())
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
