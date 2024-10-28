from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from starlette import status

from back.user_service.message_broker import rabbitmq

from back.user_service.dao import UsersDAO
from back.user_service.models import Users
from back.user_service.schemas.users import SUserCreate
from back.user_service.auth import utils as auth_utils
from back.user_service.auth.helpers import create_access_token, create_refresh_token
from back.user_service.auth.validation import (
    get_current_auth_user_for_refresh,
    validate_auth_user,
    get_current_auth_user,
)
from back.user_service.schemas.users import SUser

http_bearer = HTTPBearer(auto_error=False)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(http_bearer)],
)


@router.post("/register/", response_model=SUser)
async def user_register(
    new_user: SUserCreate,
):
    user = await UsersDAO.find_one_or_none(username=new_user.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user already exists",
        )
    new_user = new_user.model_dump()
    new_user["hashed_password"] = auth_utils.hash_password(new_user["hashed_password"])
    user: Users = await UsersDAO.insert(**new_user)
    await rabbitmq.new_user(user.id, user.username)
    return user


@router.post("/login/", response_model=TokenInfo)
async def auth_user_issue_jwt(
    user: SUser = Depends(validate_auth_user),
):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh/",
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


@router.get("/users/me/", response_model=SUser)
async def auth_user_check_self_info(
    user: SUser = Depends(get_current_auth_user),
):
    return user


@router.delete("/users")
async def user_delete(user: SUser = Depends(get_current_auth_user)):
    await UsersDAO.delete(user.id)
    await rabbitmq.delete_user(user.id)
    return {"message": "user deleted"}
